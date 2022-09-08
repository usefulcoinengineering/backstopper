#!/usr/bin/env python3
#
# library name: stopper.py
# library author: munair simpson
# library created: 20220819
# library purpose: submit a stop-limit order to the orderbook with the Gemini REST API

import requests
import datetime
import time

from backstopper.logging.logger import logger as logger
from backstopper.messaging.messenger import sendmessage as sendmessage

import backstopper.informing.definer as definer
import backstopper.authenticating.authenticator as authenticator

def askstoplimit(
        pair : str,
        size : str,
        stop : str,
        sell : str
    ) -> str :

    # Construct stop loss order payload.
    # Note that sell orders require the stop_price to be greater than the price.
    endpoint = '/v1/order/new'
    t = datetime.datetime.now()
    payload = {
        'request': endpoint,
        'nonce': str( int ( time.mktime( t.timetuple() ) * 1000 ) ),
        'symbol': pair,
        'amount': size,
        'stop_price': stop,
        'price': sell,
        'side': 'sell',
        'type': 'exchange stop limit'
    }
    headers = authenticator.authenticate(payload)

    request = definer.restserver + endpoint
    response = requests.post(request, data = None, headers = headers['restheader'])
    
    return response