#!/usr/bin/env python3
#
# library name: closevalidator.py
# library author: munair simpson
# library created: 20220817
# library purpose: continually monitor trade prices via Gemini's Websockets API until the exit threshold is breached.

import ssl
import json
import time
import asyncio
import datetime
import websockets

from backstopper.logging.logger import logger as logger
from backstopper.messaging.messenger import sendmessage as sendmessage
from backstopper.authenticating.authenticator import authenticate as authenticator

async def confirmexecution (
        order : str
    ) -> None :

    # Request trade data only.
    urlrequest = "wss://api.gemini.com/v1/order/events"
    parameters = "?eventTypeFilter=closed"
    connection = urlrequest + parameters

    # Construct payload.
    t = datetime.datetime.now()
    endpoint = '/v1/order/events'
    nonce = str( int ( time.mktime( t.timetuple() ) * 1000 ) )
    payload = {
        'request': endpoint,
        'nonce': nonce
    }
    header = authenticator.authenticate(payload)

    # Introduce function.
    logger.info(f'Looping while {order} is live (i.e. active and not "closed") on Gemini\'s orderbook... ')

    keeplooping = True

    async with websockets.connect( connection, extra_headers=header['sockheader'] ) as websocket:
        while keeplooping :
            message = await websocket.recv()
            # Remove comment to debug with: logger.debug( message )
            # Load update into a dictionary.
            dictionary = json.loads( message )

            # Check arrays for order.
            if isinstance(dictionary, list):
                for closedevent in dictionary:
                    if closedevent['order_id'] == order : 
                        infomessage = f'Completed the {closedevent["order_type"]} {closedevent["side"]}ing of '
                        infomessage = infomessage + f'{closedevent["executed_amount"]} {closedevent["symbol"].upper()[:3]} '
                        infomessage = infomessage + f'for {closedevent["price"]} {closedevent["symbol"].upper()[3:]}. '
                        logger.info( infomessage )
                        sendmessage( infomessage )
                        keeplooping = False
            else: 
                # Display heartbeat
                if dictionary[ 'type' ] == "heartbeat" : logger.debug ( f'Heartbeat: {dictionary[ "socket_sequence" ]}' )
