#!/usr/bin/env python3


import requests
import datetime
import time

from decimal import Decimal

from backstopper.logging.logger import logger as logger

import backstopper.informing.definer as definer
import backstopper.authenticating.authenticator as authenticator

def bidorder (
        pair: str,
        size: str,
        last: str
    ) -> str :

    # Construct buy order payload.
    # Use 'options': ['maker-or-cancel'] for post only orders.
    endpoint = '/v1/order/new'
    t = datetime.datetime.now()
    payload = {
        'request': endpoint,
        'nonce': str(int(time.mktime(t.timetuple())*1000)),
        'symbol': pair,
        'amount': size,
        'price': str(last),
        'side': 'buy',
        'type': 'exchange limit',
        'options': ['maker-or-cancel']
    }
    headers = authenticator.authenticate(payload)

    request = definer.restserver + endpoint
    response = requests.post(request, data = None, headers = headers['restheader'])

    return response

def quotabid (
        pair: str,
        cash: str,
        cost: str
    ) -> str :

    # Determine API transaction fee.
    # Refer to https://docs.gemini.com/rest-api/#basis-point.
    # Fees are calculated on the notional value of each trade (price × size).
    # Meaning (for API transactions): size * price * 1.001 = cash
    fraction = Decimal( definer.apitransactionfee )
    notional = Decimal(cash) / Decimal( 1 + fraction )

    # Determine minimum order size (let's call it a tock).
    list = definer.minimumorders
    item = [ item['minimumorder'] for item in list if item['currency'] == pair[:3] ]
    tock = Decimal( item[0] )

    # Determine bid size.
    quantity = str( Decimal( notional / Decimal(cost) ).quantize( tock ) )
    bidprice = str(cost)

    # Update logs.
    logger.debug(f'bidprice: {bidprice}')
    logger.debug(f'quantity: {quantity}')

    # Construct buy order payload.
    # Use 'options': ['maker-or-cancel'] for post only orders.
    endpoint = '/v1/order/new'
    t = datetime.datetime.now()
    payload = {
        'request': endpoint,
        'nonce': str(int(time.mktime(t.timetuple())*1000)),
        'symbol': pair,
        'amount': quantity,
        'price': bidprice,
        'side': 'buy',
        'type': 'exchange limit',
        'options': ['maker-or-cancel']
    }
    headers = authenticator.authenticate(payload)

    request = definer.restserver + endpoint
    response = requests.post(request, data = None, headers = headers['restheader'])

    return response

def askorder (
        pair: str,
        size: str,
        last: str
    ) -> str :

    # Construct buy order payload.
    # Use 'options': ['maker-or-cancel'] for post only orders.
    endpoint = '/v1/order/new'
    t = datetime.datetime.now()
    payload = {
        'request': endpoint,
        'nonce': str(int(time.mktime(t.timetuple())*1000)),
        'symbol': pair,
        'amount': size,
        'price': str(last),
        'side': 'sell',
        'type': 'exchange limit',
        'options': ['maker-or-cancel']
    }
    headers = authenticator.authenticate(payload)

    request = definer.restserver + endpoint
    response = requests.post(request, data = None, headers = headers['restheader'])

    return response

def quotaask (
        pair: str,
        cash: str,
        cost: str
    ) -> str :

    # Determine API transaction fee.
    # Refer to https://docs.gemini.com/rest-api/#basis-point.
    # Fees are calculated on the notional value of each trade (price × size).
    # Meaning (for API transactions): size * price * 1.001 = cash
    fraction = Decimal( definer.apitransactionfee )
    notional = Decimal(cash) / Decimal( 1 + fraction )

    # Determine minimum order size (let's call it a tock).
    list = definer.minimumorders
    item = [ item['minimumorder'] for item in list if item['currency'] == pair[:3] ]
    tock = Decimal( item[0] )

    # Determine bid size.
    quantity = str( Decimal( notional / Decimal(cost) ).quantize( tock ) )
    askprice = str(cost)

    # Update logs.
    logger.debug(f'askprice: {askprice}')
    logger.debug(f'quantity: {quantity}')

    # Construct sell order payload.
    # Use 'options': ['maker-or-cancel'] for post only orders.
    endpoint = '/v1/order/new'
    t = datetime.datetime.now()
    payload = {
        'request': endpoint,
        'nonce': str(int(time.mktime(t.timetuple())*1000)),
        'symbol': pair,
        'amount': quantity,
        'price': askprice,
        'side': 'sell',
        'type': 'exchange limit',
        'options': ['maker-or-cancel']
    }
    headers = authenticator.authenticate(payload)

    request = definer.restserver + endpoint
    response = requests.post(request, data = None, headers = headers['restheader'])

    return response
