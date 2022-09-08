#!/usr/bin/env python3
#
# library name: trademonitor.py
# library author: munair simpson
# library created: 20220831
# library purpose: continually monitor trade prices via Gemini's Websockets API until the exit threshold is breached.


import sys
import json
import asyncio
import websockets

from decimal import Decimal

from backstopper.logging.logger import logger as logger
from backstopper.messaging.messenger import sendmessage as sendmessage

async def blockpricerange(
        marketpair: str,
        upperbound: str,
        lowerbound: str
    ) -> str : # Annotate that the return value of this function a dictionary (i.e. string type).
    
    # Cast as decimals.
    upperbound = Decimal( upperbound )
    lowerbound = Decimal( lowerbound )

    # Request trade data only.
    urlrequest = "wss://api.gemini.com/v1/marketdata/" + marketpair.lower()
    parameters = "?trades=true&heartbeat=true"
    connection = urlrequest + parameters

    # Introduce function.
    logger.info(f'Looping while {marketpair[:3]} prices are between {lowerbound:,.2f} {marketpair[3:]} and {upperbound:,.2f} {marketpair[3:]}')

    keeplooping = True

    async with websockets.connect(connection) as websocket:
        while keeplooping :
            message = await websocket.recv()
            # Remove comment to debug with: logger.debug( message )
            # Load update into a dictionary.
            dictionary = json.loads( message )

            # Display heartbeat
            if dictionary[ 'type' ] == "heartbeat" : logger.debug ( f'Heartbeat: {dictionary[ "socket_sequence" ]}' )
            else :

                # Define events array/list.
                events = dictionary[ 'events' ]
                if events == [] : 
                    logger.debug( f'No update events. Received: {message}  ' )
                else:
                    # Verify the array of events is a list.
                    # Iterate through each event in the update.
                    if isinstance ( events, list ):
                        for event in events:
                            tradeprice = Decimal( event[ 'price' ] )
                            tradevalue = Decimal( event[ 'amount' ] )
                            amountless = Decimal( 100 * ( upperbound - tradeprice ) / upperbound )
                            amountmore = Decimal( 100 * ( tradeprice - lowerbound ) / lowerbound )
                            tradevalue = Decimal( tradevalue * tradeprice ).quantize( tradeprice )
                            if event['makerSide'] == "ask" : takeraction = "increase"
                            if event['makerSide'] == "bid" : takeraction = "decrease"
                            infomessage = f'[{amountless:.2f}% below {upperbound:,.2f} {marketpair[3:]} upper bound] '
                            infomessage = infomessage + f'[{amountmore:.2f}% above {lowerbound:,.2f} {marketpair[3:]} lower bound] '
                            infomessage = infomessage + f'{tradeprice:,.2f} {marketpair[3:]} {event["makerSide"]} price taken to '
                            infomessage = infomessage + f'quickly {takeraction} {marketpair[:3]} hoard by {tradevalue:,.2f} {marketpair[3:]}. '
                            logger.info ( f'{infomessage}' )
                            if event['makerSide'] == "ask" : 
                                if lowerbound.compare( tradeprice ) == 1 : 
                                    infomessage = f'{lowerbound:,.2f} {marketpair[3:]} lower/ask price bound breached. '
                                    keeplooping = False
                            if event['makerSide'] == "bid" : 
                                if tradeprice.compare( upperbound ) == 1 : 
                                    infomessage = f'{upperbound:,.2f} {marketpair[3:]} upper/bid price bound breached. '
                                    keeplooping = False
        logger.info ( infomessage )
        sendmessage ( infomessage )
        return event # Dictionary.

if __name__ == "__main__":

    # Set default trading pair and loop exit price in case a BASH wrapper has not been used.
    marketpair = "ETHUSD"
    upperbound = "1500"
    lowerbound = "1400"

    # Override defaults with command line parameters from BASH wrapper.
    if len ( sys.argv ) == 4 :
        marketpair = sys.argv[1]
        upperbound = sys.argv[2]
        lowerbound = sys.argv[3]
    else :
        logger.warning ( f'incorrect number of command line arguments. using default values...' )
        logger.warning ( f'marketpair: {marketpair}' )
        logger.warning ( f'upperbound: {upperbound}' )
        logger.warning ( f'lowerbound: {lowerbound}' )

    try: # Enter price monitor loop.
        messageresponse = asyncio.run (
            blockpricerange (
                marketpair, 
                upperbound, 
                lowerbound 
            )
        )
    except KeyboardInterrupt: pass

    logger.info ( f'{messageresponse["price"]} is out of bounds. ') # Report status.