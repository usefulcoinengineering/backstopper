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
from backstopper.informing.tickerdigger import ticker
from backstopper.ordering.ordermanager import islive
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
pair = 'ETHUSD'
size = '0.0001'
stop = '0.0100'
sell = '0.0200'

# Override defaults with command line parameters from BASH wrapper.
if len(sys.argv) == 5:
    pair = sys.argv[1]
    size = sys.argv[2]
    stop = sys.argv[3]
    sell = sys.argv[4]
else: 
    logger.warning ( f'Incorrect number of command line arguments. Using default values for {pair} trailing...' )

# Cast decimals.
size = Decimal( size )
stop = Decimal( stop )
sell = Decimal( sell )

# Make sure "sell" is more than "stop".
# Gemini requires this for stop ask orders:
# The stop price must exceed the sell price.
if stop.compare( sell ) == 1:
    notification = f'The sell price discount {sell*100}* cannot be larger than the stop price discount {stop*100}%. '
    logger.error ( f'{notification}' )
    sys.exit(1)

# Determine tick size.
item = [ item['tick'] for item in ticksizes if item['currency'] == pair[:3] ]
tick = Decimal( item[0] )

# Determine Gemini API transaction fee. Conversion from basis points required.
geminiapifee = Decimal( 0.0001 ) * Decimal ( notionalvolume().json()["api_maker_fee_bps"] )

# Submit limit bid order, report response, and verify submission.
logger.debug ( f'Submitting {pair} frontrunning limit bid order.' )

try :
    jsonresponse = bidorder( pair, size ).json()
except Exception as e :
    # Report exception.
    notification = f'While trying to submit a frontrunning limit bid order the follow error occurred: {e} '
    logger.debug ( f'{notification}Let\'s exit. Please try rerunning the code!' )
    sys.exit(1) # Exit. Continue no further.

# To debug remove comment character below:
# logger.info ( json.dumps( jsonresponse, sort_keys=True, indent=4, separators=(',', ': ') ) )

try :
    if jsonresponse["is_cancelled"] : 
        notification = f'Bid order {jsonresponse["order_id"]} was cancelled. '
        logger.debug ( '{notification} Let\'s exit. Please try rerunning the code!' )
        sys.exit(1) # Exit. Continue no further.

    else:
        infomessage = f'Bid order {jsonresponse["order_id"]} for {jsonresponse["remaining_amount"]} {jsonresponse["symbol"].upper()[:3]} '
        infomessage = infomessage + f'at {jsonresponse["price"]} {jsonresponse["symbol"].upper()[3:]} is active and booked. '
        logger.info ( infomessage )
        sendmessage ( infomessage )

except KeyError as e:
    warningmessage = f'KeyError: {e} was not present in the response from the REST API server.'
    logger.warning ( warningmessage )
    try:    
        if jsonresponse["result"] : 
            criticalmessage = f'\"{jsonresponse["reason"]}\" {jsonresponse["result"]}: {jsonresponse["message"]}'
            logger.critical ( criticalmessage ) ; sendmessage ( criticalmessage )
            sys.exit(1)

    except Exception as e:
        criticalmessage = f'Exception: {e} '
        logger.critical ( f'Unexpecter error. Unsuccessful bid order submission. {criticalmessage}' )
        sys.exit(1)

# Confirm order execution.
asyncio.run ( confirmexecution( jsonresponse["order_id"] ) )

# Define the trade cost price and cast it.
costprice = Decimal( jsonresponse["price"] )

# Calculate exit price.
exitratio = Decimal( 1 + sell + geminiapifee )
exitprice = Decimal( costprice * exitratio ).quantize( tick )

# Calculate stop price.
stopratio = Decimal( 1 - stop )
stopprice = Decimal( exitprice * stopratio ).quantize( tick )

# Calculate sell price.
sellratio = Decimal( 1 - sell - geminiapifee )
sellprice = Decimal( exitprice * sellratio ).quantize( tick )

# Calculate quote gain.
quotegain = Decimal( sellprice * size - costprice * size ).quantize( tick )
ratiogain = Decimal( 100 * sellprice * size / costprice / size - 100 ).quantize( tick )

# Validate "stop price".
if stopprice.compare( exitprice ) == 1:
    # Make sure that the "stop price" is below the purchase price (i.e. "cost price").
    notification = f'The stop order price {stopprice:,.2f} {pair[3:]} cannot exceed the future market price of {exitprice:,.2f} {pair[3:]}. '
    logger.error ( f'{notification}' ) ; sendmessage ( f'{notification}' ) ; sys.exit(1)

# Record parameters to logs.
logger.info ( f'Cost Price: {costprice}' )
logger.info ( f'Exit Price: {exitprice}' )
logger.info ( f'Stop Price: {stopprice}' )
logger.info ( f'Sell Price: {sellprice}' )
logger.info ( f'Quote Gain: {quotegain} {pair[3:]}' )
logger.info ( f'Ratio Gain: {ratiogain:.2f}%' )

# Explain the opening a websocket connection.
# Also explain the wait for an increase in the prices sellers are willing to take to rise above the "exitprice".
infomessage = f'Waiting for sellers to take {exitprice:,.2f} {pair[3:]} to rid themselves of {pair[:3]} '
infomessage = infomessage + f'[i.e. rise {Decimal( sell + geminiapifee ) * 100:,.2f}%]. '
logger.info ( f'{infomessage}' ) ; sendmessage ( f'{infomessage}' )

# Loop.
while True : # Block until the price sellers are willing to take exceeds the exitprice. 

    try: 
        # Open websocket connection. 
        # Block until out of bid price bounds (work backwards to get previous stop order's sell price).
        websocketoutput : str = asyncio.run (
            blockpricerange (
                marketpair = pair, 
                upperbound = exitprice, 
                lowerbound = -exitprice
            )
        )
    except Exception as e:
        # Report exception.
        notification = f'Error : {e} '
        logger.debug ( f'{notification}Let\'s reestablish the connection and try again! ' )
        time.sleep(3) # Sleep for 3 seconds since we are interfacing with a rate limited Gemini REST API.
        continue # Restart while loop logic.
    logger.info ( f'{Decimal( websocketoutput["price"] ).quantize( tick ):,.2f} is out of bounds. ') # Report status.
    break # Break out of the while loop because the subroutine ran successfully.

# Loop.
while True : # Block until achieving the successful submission of an initial stop limit ask order. 
        
    # Submit initial Gemini "stop-limit" order. 
    # If in doubt about what's going on, refer to documentation here: https://docs.gemini.com/rest-api/#new-order.
    notification = f'Submitting initial stop-limit (ask) order with a {stopprice:,.2f} {pair[3:]} stop. '
    notification = notification + f'This stop limit order has a {sellprice:,.2f} {pair[3:]} limit price to sell {size} {pair[:3]}. '
    notification = notification + f'Resulting in a {ratiogain:,.2f}% gain if executed. '
    logger.debug ( f'{notification}' ) ; sendmessage ( f'{notification}' )
    try:    
        jsonresponse = askstoplimit( str(pair), str(size), str(stopprice), str(sellprice) ).json()
    except Exception as e:
        logger.info ( f'Unable to get information on ask stop limit order. Error: {e}' )
        time.sleep(3) # Sleep for 3 seconds since we are interfacing with a rate limited Gemini REST API.
        continue # Keep trying to submit ask stop limit order.
    jsondeposits = json.dumps( jsonresponse, sort_keys=True, indent=4, separators=(',', ': ') )
    logger.debug ( f'\n{jsondeposits}' )
    time.sleep(3) # Sleep for 3 seconds since we are interfacing with a rate limited Gemini REST API.
    break # Break out of the while loop because the subroutine ran successfully.

# Loop.
while True : # Block until order status has been determined. 

    time.sleep(3) # Sleep for 3 seconds since we are interfacing with a rate limited Gemini REST API.
    
    try:
        orderstatus = islive( jsonresponse["order_id"] ).json() # Post REST API call to determine order's status.
    except Exception as e:
        logger.info ( f'Unable to retrieve stop limit order status. Error: {e}' )
        time.sleep(3) # Sleep for 3 seconds since we are interfacing with a rate limited Gemini REST API.
        continue # Keep trying to get information on the order's status infinitely.
    try:
        if orderstatus['is_live'] : 
            logger.info( f'Initial stop limit order {orderstatus["order_id"]} is live on the Gemini orderbook. ' )
            jsonresponse = orderstatus # Assign orderstatus to the jsonresponse used subsequently.
            break # Break out of the while loop because we want to reset the stop order as prices rise.
        else : 
            logger.info( f'Initial stop limit order {orderstatus["order_id"]} is NOT live on the Gemini orderbook. ' )
            jsonresponse = orderstatus # Assign orderstatus to the jsonresponse used subsequently.
            break # Break out of the while loop because the subroutine ran successfully.
    except KeyError as e:
        warningmessage = f'KeyError: {e} was not present in the response from the REST API server. '
        logger.warning ( f'{warningmessage} Something went wrong.. Checking for an error message...' )
        try:    
            if orderstatus["result"] : 
                logger.warning ( f'\"{orderstatus["reason"]}\" {orderstatus["result"]}: {orderstatus["message"]}' )
                continue
        except Exception as e:
            criticalmessage = f'Exception: {e} '
            logger.critical ( f'Unexpecter error. {criticalmessage}' ) ; sendmessage ( f'Unexpecter error. {criticalmessage}' )
            time.sleep(3) # Sleep for 3 seconds since we are interfacing with a rate limited Gemini REST API.
            continue

# Counter.
iteration = 0

# Loop.
while True : # Block until prices rise (then cancel and resubmit stop limit order) or block until a stop limit ask order was "closed". 

    # Augment counter.
    iteration = iteration + 1
    logger.debug ( iteration )

    # Break out of loop if order "closed".
    if not jsonresponse["is_live"] : break

    # Explain upcoming actions.
    logger.debug ( f'Changing exitratio from {exitratio} to {Decimal( 1 + stop + geminiapifee )}. ')
    logger.debug ( f'Changing exitprice from {exitprice} to {Decimal( exitprice * exitratio ).quantize( tick )}. ')

    # Lower the exit ratio to lock gains faster.
    exitratio = Decimal( 1 + stop + geminiapifee )

    # Calculate new exit price (block until exitprice exceeded).
    exitprice = Decimal( exitprice * exitratio ).quantize( tick )

    # Recalculate quote gain.
    quotegain = Decimal( sellprice * size - costprice * size ).quantize( tick )
    ratiogain = Decimal( 100 * sellprice * size / costprice / size - 100 )

    # Loop.
    while True : # Block until prices rise (or fall to stop limit order's sell price).

        tradingpair = str(pair)
        tradingexit = str(exitprice)
        tradingsell = str(sellprice)
        try: 
            # Open websocket connection. 
            # Block until out of bid price bounds (work backwards to get previous stop order's sell price).
            websocketoutput : str = blockpricerange ( tradingpair, tradingexit, tradingsell ) 
        except Exception as e:
            # Report exception.
            notification = f'The websocket connection failed. '
            logger.debug ( f'{e}: {notification}Let\'s reestablish the connection and try again! ' )
            time.sleep(3) # Sleep for 3 seconds since we are interfacing with a rate limited Gemini REST API.
            continue # Restart while loop logic.
        logger.info ( f'{Decimal( websocketoutput["price"] ).quantize( tick ):,.2f} is out of bounds. ') # Report status.
        break # Break out of the while loop because the subroutine ran successfully.

    # Check if lower bound breached.
    # If so, the stop order will "close".
    if exitprice.compare( Decimal( websocketoutput["price"] ) ) == 1: 
        logger.debug ( f'Ask prices have fallen below the ask price of the stop limit order {jsonresponse["order_id"]}. ' )
        logger.debug ( f'The stop order at {sellprice} {pair[3:]} should have been completely filled and now "closed". ' )
        break # The stop limit order should have been executed.
    else:
        exitprice = Decimal( websocketoutput["price"] ) # Set the exit price to the websocketoutput price and continue.

    # Explain upcoming actions.
    logger.debug ( f'Changing stopprice from {stopprice} to {Decimal( exitprice * stopratio ).quantize( tick )}. ')
    logger.debug ( f'Changing sellprice from {sellprice} to {Decimal( exitprice * sellratio ).quantize( tick )}. ')

    # Calculate new sell/stop prices.
    stopprice = Decimal( exitprice * stopratio ).quantize( tick )
    sellprice = Decimal( exitprice * sellratio ).quantize( tick )
    # Note: "costprice" is no longer the basis of the new exit price (and thus stop and sell prices).
    # Note: The last transaction price exceeds the previous exit price and creates the new exit price.

    # Loop.
    while True : # Block until existing stop order is cancelled. 

        # Attempt to cancel active and booked stop limit (ask) order.
        logger.debug ( f'Going to try to cancel stop limit order {jsonresponse["order_id"]} in three seconds...' )
        time.sleep(3) # Sleep for 3 seconds since we are interfacing with a rate limited Gemini REST API.

        try:
            jsonresponse = cancelorder( jsonresponse["order_id"] ).json() # Post REST API call to cancel previous order.
        except Exception as e:
            logger.info ( f'Unable to cancel order. Error: {e}' )
            time.sleep(3) # Sleep for 3 seconds since we are interfacing with a rate limited Gemini REST API.
            continue # Keep trying to get information on the order's status infinitely.
        logger.info = f'Cancelled {jsonresponse["price"]} {pair[3:]} stop sell order {jsonresponse["order_id"]}. '
        break

    # Loop.
    while True : # Block until a new stop limit order is submitted. 

        while True: # Block until present highest bid price information is attained. 
            try:
                # Get highest bid price.
                # You can only sell for less.
                highestbid = Decimal( ticker( pair )["bid"] )
            except Exception as e:
                logger.debug( f'An exception occured when trying to retrieve the price ticker. Error: {e}' )
                time.sleep(3) # Sleep for 3 seconds since we are interfacing with a rate limited Gemini REST API.
                continue
            break


        # Validate "stop price".
        # Make sure that the bids exceed it.
        # Otherwise the order wont be accepted.
        if highestbid.compare( exitprice ) == 1:

            # Post updated stop-limit order.
            logger.info = f'Submitting stop-limit (ask) order with a {stopprice:,.2f} {pair[3:]} stop {sellprice:,.2f} {pair[3:]} sell. '
            logger.info = f'There will be an unrealized (i.e. "ratio gain") {ratiogain:,.2f}% profit/loss of {quotegain:,.2f} {pair[3:]} '
            # sendmessage ( f'Submitting {stopprice:,.2f} {pair[3:]} stop {sellprice:,.2f} {pair[3:]} sell limit order. ' )
            # sendmessage ( f'That would realize {quotegain:,.2f} {pair[3:]} [i.e. return {ratiogain:,.2f}%]. ' )
            try:
                jsonresponse = askstoplimit( str(pair), str(size), str(stopprice), str(sellprice) ).json()
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
quotegain = Decimal( sellprice * size - costprice * size ).quantize( tick )
ratiogain = Decimal( 100 * sellprice * size / costprice / size - 100 )

# Report profit/loss.
clause0 = f'There was a {ratiogain:,.2f}% profit/loss of {quotegain:,.2f} {pair[3:]} '
clause1 = f'from the sale of {size} {pair[:3]} at {Decimal(sellprice * size):,.2f} {pair[3:]} '
clause2 = f'which cost {Decimal(costprice * size):,.2f} {pair[3:]} to acquire.'
message = f'{clause0}{clause1}{clause2}'
logger.info ( message ) ; sendmessage ( message )

# Let the shell know we successfully made it this far!
sys.exit(0)