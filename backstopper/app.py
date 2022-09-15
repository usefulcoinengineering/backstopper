#!/usr/bin/env python3
#
# script name: backstopper.py
# script author: munair simpson
# script created: 20220816
# script purpose: buy the asset specified then sell it using a highest bid trailing stop-limit ask.


# Strategy Outline:
#  1. Buy BTC (by default) almost at the market price using the REST API (with a frontrunning USD bid).
#  2. Open a websocket connection and wait for confirmation that submitted bid order was filled.
#  3. Capture the price of the executed order and use it to calculate the last price that should trip the submission of a stop-limit order.
#  4. Monitor last price data until the transaction price exceeds the price target. 
#  5. Submit the initial stop limit order to sell BTC. If this order fills, exit. Otherwise, monitor prices for increases.
#  6. On the occasion that last price exceeds a new price target, cancel the old stop limit order and submit an updated stop-limit order to sell when the new price target is reached.
#  7. On the occasion that monitored ask prices indicate that the existing stop limit order should close, stop monitoring prices and exit.
#
# Execution:
#   - Use the wrapper BASH script in the "strategies" directory.

import sys
import json
import time
import asyncio

from decimal import Decimal

from backstopper.informing.definer import ticksizes

from backstopper.logging.logger import logger
from backstopper.ordering.frontrunner import bidorder
from backstopper.ordering.stopper import askstoplimit
from backstopper.ordering.ordermanager import cancelorder
from backstopper.informing.volumizer import notionalvolume
from backstopper.monitoring.trademonitor import blockpricerange
from backstopper.monitoring.closevalidator import confirmexecution
from backstopper.messaging.messenger import sendmessage as sendmessage

# Set bid size in the base currency (BTC in this case).
# This amount should exceed ~25 cents ['0.00001' is the minimum for BTCUSD].
# You will accumulate gains in the quote currency (USD in this case). This amount is called the "quotegain".
# Specify the percentage discount off the market price that determines the stop price desired in decimal terms (for example 100 basis points).
# Specify the percentage discount off the market price that determines the sell price desired in decimal terms (for example 200 basis points).
# Makes sure both price deltas, exceed the Gemini API fee if you want this to execute profitably. For example, 20 basis points (or '0.002').
currencypair : str = 'ETHUSD'
longquantity : str = '0.0001'
stopdiscount : str = '0.0100'
selldiscount : str = '0.0200'

# Override defaults with command line parameters from BASH wrapper.
if len(sys.argv) == 5 :
    currencypair = sys.argv[1]
    longquantity = sys.argv[2]
    stopdiscount = sys.argv[3]
    selldiscount = sys.argv[4]
else : 
    logger.warning ( f'Incorrect number of command line arguments. Using default values for {currencypair} trailing...' )

# Cast strings.
quotecurrency : str = currencypair[3:]
assetcurrency : str = currencypair[:3]

# Cast decimals.
tradesize = Decimal( longquantity )
stopinput = Decimal( stopdiscount )
sellinput = Decimal( selldiscount )

# Make sure "sell" is more than "stop".
# Gemini requires this for stop ask orders:
# The stop price must exceed the sell price.
if stopinput.compare( sellinput ) == 1 :
    notification = f'The sell price discount {sellinput*100}* cannot be larger than the stop price discount {stopinput*100}%. '
    logger.error ( f'{notification}' )
    sys.exit(1)

# Determine tick size.
item = [ item['tick'] for item in ticksizes if item['currency'] == assetcurrency ]
tick = Decimal( item[0] )

# Determine Gemini API transaction fee. Conversion from basis points required.
geminiapifee = Decimal( 0.0001 ) * Decimal ( notionalvolume().json()["api_maker_fee_bps"] )

# Submit limit bid order, report response, and verify submission.
logger.debug ( f'Submitting {currencypair} frontrunning limit bid order.' )

try :
    jsonresponse = bidorder( currencypair, longquantity ).json()
except Exception as e :
    # Report exception.
    notification = f'While trying to submit a frontrunning limit bid order the follow error occurred: {e} '
    logger.debug ( f'{notification}Let\'s exit. Please try rerunning the code! ' )
    sys.exit(1) # Exit. Continue no further.

# To debug remove comment character below:
# logger.info ( json.dumps( jsonresponse, sort_keys=True, indent=4, separators=(',', ': ') ) )

try :
    if jsonresponse["is_cancelled"] : 
        notification = f'Bid order {jsonresponse["order_id"]} was cancelled. '
        logger.debug ( '{notification} Let\'s exit. Please try rerunning the code!' )
        sys.exit(1) # Exit. Continue no further.

    else :
        infomessage = f'Bid order {jsonresponse["order_id"]} for {jsonresponse["remaining_amount"]} {jsonresponse["symbol"].upper()[:3]} '
        infomessage = infomessage + f'at {jsonresponse["price"]} {jsonresponse["symbol"].upper()[3:]} is active and booked. '
        logger.info ( infomessage )
        sendmessage ( infomessage )

except KeyError as e :
    warningmessage = f'KeyError : {e} was not present in the response from the REST API server.'
    logger.warning ( warningmessage )
    try :    
        if jsonresponse["result"] : 
            criticalmessage = f'\"{jsonresponse["reason"]}\" {jsonresponse["result"]}: {jsonresponse["message"]}'
            logger.critical ( criticalmessage ) ; sendmessage ( criticalmessage )
            sys.exit(1)

    except Exception as e :
        criticalmessage = f'Exception : {e} '
        logger.critical ( f'Unexpecter error. Unsuccessful bid order submission. {criticalmessage}' )
        sys.exit(1)

# Confirm order execution.
asyncio.run ( confirmexecution( jsonresponse["order_id"] ) )

# Define the trade cost price and cast it.
costprice = Decimal( jsonresponse["price"] )

# Calculate exit price.
exitratio = Decimal( 1 + sellinput + geminiapifee )
exitprice = Decimal( costprice * exitratio ).quantize( tick )

# Calculate stop price.
stopratio = Decimal( 1 - stopinput )
stopprice = Decimal( exitprice * stopratio ).quantize( tick )

# Calculate sell price.
sellratio = Decimal( 1 - sellinput - geminiapifee )
sellprice = Decimal( exitprice * sellratio ).quantize( tick )

# Calculate quote gain.
quotegain = Decimal( sellprice * tradesize - costprice * tradesize ).quantize( tick )
ratiogain = Decimal( 100 * sellprice * tradesize / costprice / tradesize - 100 ).quantize( tick )

# Validate "stop price".
if stopprice.compare( exitprice ) == 1:
    # Make sure that the "stop price" is below the purchase price (i.e. "cost price").
    notification = f'The stop order price {stopprice:,.2f} {quotecurrency} cannot exceed the future market price of {exitprice:,.2f} {quotecurrency}. '
    logger.error ( f'{notification}' ) ; sendmessage ( f'{notification}' ) ; sys.exit(1)

# Record parameters to logs.
logger.info ( f'Cost Price: {costprice}' )
logger.info ( f'Exit Price: {exitprice}' )
logger.info ( f'Stop Price: {stopprice}' )
logger.info ( f'Sell Price: {sellprice}' )
logger.info ( f'Quote Gain: {quotegain} {quotecurrency}' )
logger.info ( f'Ratio Gain: {ratiogain:.2f}%' )

# Explain the opening a websocket connection.
# Also explain the wait for an increase in the prices sellers are willing to take to rise above the "exitprice".
infomessage = f'Waiting for sellers to take {exitprice:,.2f} {quotecurrency} to rid themselves of {assetcurrency} '
infomessage = infomessage + f'[i.e. rise {Decimal( sellinput + geminiapifee ) * 100:,.2f}%]. '
logger.info ( f'{infomessage}' ) ; sendmessage ( f'{infomessage}' )

# Loop.
while True : # Block until the price sellers are willing to take exceeds the exitprice. 

    try: 
        # Open websocket connection. 
        # Block until out of bid price bounds (work backwards to get previous stop order's sell price).
        websocketoutput : str = asyncio.run (  blockpricerange ( currencypair,  str(exitprice), str(-exitprice) ) )
    except Exception as e:
        # Report exception.
        notification = f'Error : {e} '
        logger.debug ( f'{notification}Let\'s reestablish the connection and try again! ' )
        time.sleep(3) # Sleep for 3 seconds since we are interfacing with a rate limited Gemini REST API.
        continue # Restart while loop logic.
    else:
        logger.info ( f'{Decimal( websocketoutput["price"] ).quantize( tick ):,.2f} is out of bounds. ') # Report status.
        break # Break out of the while loop because the subroutine ran successfully.

# Loop.
while True : # Block until achieving the successful submission of an initial stop limit ask order. 
        
    # Submit initial Gemini "stop-limit" order. 
    # If in doubt about what's going on, refer to documentation here: https://docs.gemini.com/rest-api/#new-order.
    notification = f'Submitting initial stop-limit (ask) order with a {stopprice:,.2f} {quotecurrency} stop. '
    notification = notification + f'This stop limit order has a {sellprice:,.2f} {quotecurrency} limit price to '
    notification = notification + f'sell {longquantity} {assetcurrency}. Resulting in a {ratiogain:,.2f}% gain if executed. '
    logger.debug ( f'{notification}' ) ; sendmessage ( f'{notification}' )
    
    try :    
        jsonresponse = askstoplimit( currencypair, longquantity, str(stopprice), str(sellprice) ).json()
    except Exception as e :
        logger.info ( f'Unable to get information on ask stop limit order. Error: {e}' )
        time.sleep(3) # Sleep for 3 seconds since we are interfacing with a rate limited Gemini REST API.
        continue # Keep trying to submit ask stop limit order.
    else :
        logger.debug ( f'\n{json.dumps( jsonresponse, sort_keys=True, indent=4, separators=(",", ": ") )} ' )
        if jsonresponse['is_live'] :
            logger.info( f'Initial stop limit order {jsonresponse["order_id"]} is live on the Gemini orderbook. ' )
            break # Break out of the while loop because the subroutine ran successfully.

# Loop.
while True : # Block until prices rise (then cancel and resubmit stop limit order) or block until a stop limit ask order was "closed". 

    # Break out of loop if order "closed".
    if not jsonresponse["is_live"] : break

    # Explain upcoming actions.
    logger.debug ( f'Changing exitratio from {exitratio} to {Decimal( 1 + stopinput + geminiapifee )}. ')
    logger.debug ( f'Changing exitprice from {exitprice} to {Decimal( exitprice * exitratio ).quantize( tick )}. ')

    # Lower the exit ratio to lock gains faster.
    exitratio = Decimal( 1 + stopinput + geminiapifee )

    # Calculate new exit price (block until exitprice exceeded).
    exitprice = Decimal( exitprice * exitratio ).quantize( tick )

    # Recalculate quote gain.
    quotegain = Decimal( sellprice * tradesize - costprice * tradesize ).quantize( tick )
    ratiogain = Decimal( 100 * sellprice * tradesize / costprice / tradesize - 100 )

    # Loop.
    while True : # Block until prices rise (or fall to stop limit order's sell price).

        try : 
            # Open websocket connection. 
            # Block until out of bid price bounds (work backwards to get previous stop order's sell price).
            websocketoutput : str = asyncio.run ( blockpricerange ( str(currencypair), str(exitprice), str(sellprice) ) )
        except Exception as e :
            # Report exception.
            notification = f'The websocket connection failed. '
            logger.debug ( f'{e} : {notification}Let\'s reestablish the connection and try again! ' )
            time.sleep(3) # Sleep for 3 seconds since we are interfacing with a rate limited Gemini REST API.
            continue # Restart while loop logic.
        else :
            lastprice = Decimal( websocketoutput["price"] ) # Define last price.
            logger.info ( f'{lastprice.quantize( tick ):,.2f} {quotecurrency} is out of bounds. ') # Report status.
            break # Break out of the while loop because the subroutine ran successfully.

    # Check if lower bound breached.
    # If so, the stop order will "close".
    if exitprice.compare( lastprice ) == 1 : 
        logger.debug ( f'Ask prices have fallen below the ask price of the stop limit order {jsonresponse["order_id"]}. ' )
        logger.debug ( f'The stop order at {sellprice} {quotecurrency} should have been completely filled and now "closed". ' )
        break # The stop limit order should have been executed.
    
    # Loop.
    while True : # Block until existing stop order is cancelled. 

        # Attempt to cancel active and booked stop limit (ask) order.
        logger.debug ( f'Going to try to cancel stop limit order {jsonresponse["order_id"]}...' )

        try :
            jsonresponse = cancelorder( jsonresponse["order_id"] ).json() # Post REST API call to cancel previous order.
        except Exception as e :
            logger.debug ( f'Unable to cancel order. Error: {e}' )
            time.sleep(3) # Sleep for 3 seconds since we are interfacing with a rate limited Gemini REST API.
            continue # Keep trying to get information on the order's status infinitely.
        else :
            logger.debug = f'Cancelled {jsonresponse["price"]} {quotecurrency} stop sell order {jsonresponse["order_id"]}. '
            break

    # Explain upcoming actions.
    explanation  = f'\nRecalculate stop and sell pricing based on the last price {lastprice} {quotecurrency}. \n'
    explanation += f'Changing stopprice from {stopprice} to {Decimal( lastprice * stopratio ).quantize( tick )}. \n'
    explanation += f'Changing sellprice from {sellprice} to {Decimal( lastprice * sellratio ).quantize( tick )}. \n'
    logger.info ( explanation )
    
    # Calculate new sell/stop prices.
    stopprice = Decimal( lastprice * stopratio ).quantize( tick )
    sellprice = Decimal( lastprice * sellratio ).quantize( tick )
    # Note : "costprice" is no longer the basis of the new exit price (and thus stop and sell prices).
    # Note : The last transaction price exceeds the previous exit price and creates the new exit price.

    # Loop.
    while True : # Block until a new stop limit order is submitted. 

        # Post updated stop-limit order.
        logger.info = f'Submitting stop-limit (ask) order with a {stopprice:,.2f} {quotecurrency} stop {sellprice:,.2f} {quotecurrency} sell. '
        logger.info = f'There will be an unrealized (i.e. "ratio gain") {ratiogain:,.2f}% profit/loss of {quotegain:,.2f} {quotecurrency} '
        # sendmessage ( f'Submitting {stopprice:,.2f} {quotecurrency} stop {sellprice:,.2f} {quotecurrency} sell limit order. ' )
        # sendmessage ( f'That would realize {quotegain:,.2f} {quotecurrency} [i.e. return {ratiogain:,.2f}%]. ' )
        try:
            jsonresponse = askstoplimit( currencypair, longquantity, str(stopprice), str(sellprice) ).json()
            """
                Response format expected:
                    {
                        "order_id": "7419662",
                        "id": "7419662",
                        "symbol": "btcusd",
                        "exchange": "gemini",
                        "avg_execution_price": "0.00",
                        "side": "buy",
                        "type": "stop-limit",
                        "timestamp": "1572378649",
                        "timestampms": 1572378649018,
                        "is_live": True,
                        "is_cancelled": False,
                        "is_hidden": False,
                        "was_forced": False,
                        "executed_amount": "0",
                        "options": [],
                        "stop_price": "10400.00",
                        "price": "10500.00",
                        "original_amount": "0.01"
                    }
            """
        except Exception as e:
            logger.debug ( f'Unable to get information on the stop-limit order cancellation request. Error: {e}' )
            time.sleep(3) # Sleep for 3 seconds since we are interfacing with a rate limited Gemini REST API.
            continue # Keep trying to post stop limit order infinitely.
        break

# Recalculate quote gain.
quotegain = Decimal( sellprice * tradesize - costprice * tradesize ).quantize( tick )
ratiogain = Decimal( 100 * sellprice * tradesize / costprice / tradesize - 100 )

# Report profit/loss.
clause0 = f'There was a {ratiogain:,.2f}% profit/loss of {quotegain:,.2f} {quotecurrency} '
clause1 = f'from the sale of {tradesize} {assetcurrency} at {Decimal(sellprice * tradesize):,.2f} {quotecurrency} '
clause2 = f'which cost {Decimal(costprice * tradesize):,.2f} {quotecurrency} to acquire.'
message = f'{clause0}{clause1}{clause2}'
logger.info ( message ) ; sendmessage ( message )

# Let the shell know we successfully made it this far!
sys.exit(0)