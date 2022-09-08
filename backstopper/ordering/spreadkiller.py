#!/usr/bin/env python3


import requests
import datetime
import time

from decimal import Decimal

from backstopper.logging.logger import logger as logger

import backstopper.informing.definer as definer
import backstopper.authenticating.authenticator as authenticator

def bidorder (
        pair : str,
        size : str,
    ) -> str :

    # Determine tick size.
    list = definer.ticksizes
    item = [ item['tick'] for item in list if item['currency'] == pair[:3] ]
    tick = Decimal( item[0] )

    # Determine minimum order size (let's call it a tock).
    list = definer.minimumorders
    item = [ item['minimumorder'] for item in list if item['currency'] == pair[:3] ]
    tock = Decimal( item[0] )

    # Get the lowest ask in the orderbook.
    endpoint = '/v1/pubticker/' + pair
    response = requests.get( definer.restserver + endpoint )
    askprice = Decimal( response.json()['ask'] )
    bidprice = str( Decimal( askprice - tick ).quantize( askprice ) )
    quantity = str( Decimal( size ).quantize( tick ) )

    # Update logs.
    logger.debug(f'Askprice: {askprice}')
    logger.debug(f'Bidprice: {bidprice}')
    logger.debug(f'Quantity: {quantity}')

    # Construct buy order payload.
    # Use 'options': ['maker-or-cancel'] for post only orders.
    endpoint = '/v1/order/new'
    t = datetime.datetime.now()
    payload = {
        'request': endpoint,
        'nonce': str( int ( time.mktime( t.timetuple() ) * 1000 ) ),
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

def quotabid (
        pair : str,
        cash : str,
    ) -> str :

    # Determine API transaction fee.
    # Refer to https://docs.gemini.com/rest-api/#basis-point.
    # Fees are calculated on the notional value of each trade (price × size).
    # Meaning (for API transactions): size * price * 1.001 = cash
    fraction = Decimal( definer.apitransactionfee )
    notional = Decimal(cash) / Decimal( 1 + fraction )

    # Determine tick size.
    list = definer.ticksizes
    item = [ item['tick'] for item in list if item['currency'] == pair[:3] ]
    tick = Decimal( item[0] )

    # Determine minimum order size (let's call it a tock).
    list = definer.minimumorders
    item = [ item['minimumorder'] for item in list if item['currency'] == pair[:3] ]
    tock = Decimal( item[0] )

    # Get the lowest ask in the orderbook.
    # Then determine the bid order size.
    endpoint = '/v1/pubticker/' + pair
    response = requests.get( definer.restserver + endpoint )
    askprice = Decimal( response.json()['ask'] )
    bidprice = str( Decimal( askprice - tick ).quantize( askprice ) )
    quantity = str( Decimal( notional / Decimal(bidprice) ).quantize( tick ) )

    # Update logs.
    logger.debug(f'Askprice: {askprice}')
    logger.debug(f'Bidprice: {bidprice}')
    logger.debug(f'Quantity: {quantity}')

    # Construct buy order payload.
    # Use 'options': ['maker-or-cancel'] for post only orders.
    endpoint = '/v1/order/new'
    t = datetime.datetime.now()
    payload = {
        'request': endpoint,
        'nonce': str( int ( time.mktime( t.timetuple() ) * 1000 ) ),
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
        pair : str,
        size : str,
    ) -> str :

    # Determine tick size.
    list = definer.ticksizes
    item = [ item['tick'] for item in list if item['currency'] == pair[:3] ]
    tick = Decimal( item[0] )

    # Determine minimum order size (let's call it a tock).
    list = definer.minimumorders
    item = [ item['minimumorder'] for item in list if item['currency'] == pair[:3] ]
    tock = Decimal( item[0] )

    # Get the highest bid in the orderbook.
    endpoint = '/v1/pubticker/' + pair
    response = requests.get( definer.restserver + endpoint )
    bidprice = Decimal( response.json()['bid'] )
    askprice = str( Decimal( bidprice + tick ).quantize( bidprice ) )
    quantity = str( Decimal( size ).quantize( tick ) )

    # Update logs.
    logger.debug(f'Bidprice: {bidprice}')
    logger.debug(f'Askprice: {askprice}')
    logger.debug(f'Quantity: {quantity}')

    # Construct buy order payload.
    # Use 'options': ['maker-or-cancel'] for post only orders.
    endpoint = '/v1/order/new'
    t = datetime.datetime.now()
    payload = {
        'request': endpoint,
        'nonce': str( int ( time.mktime( t.timetuple() ) * 1000 ) ),
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

def quotaask (
        pair : str,
        cash : str,
    ) -> str :

    # Determine API transaction fee.
    # Refer to https://docs.gemini.com/rest-api/#basis-point.
    # Fees are calculated on the notional value of each trade (price × size).
    # Meaning (for API transactions): size * price * 1.001 = cash
    fraction = Decimal( definer.apitransactionfee )
    notional = Decimal(cash) / Decimal( 1 + fraction )

    # Determine tick size.
    list = definer.ticksizes
    item = [ item['tick'] for item in list if item['currency'] == pair[:3] ]
    tick = Decimal( item[0] )

    # Determine minimum order size (let's call it a tock).
    list = definer.minimumorders
    item = [ item['minimumorder'] for item in list if item['currency'] == pair[:3] ]
    tock = Decimal( item[0] )

    # Get the highest bid in the orderbook.
    # Then determine the ask order size.
    endpoint = '/v1/pubticker/' + pair
    response = requests.get( definer.restserver + endpoint )
    bidprice = Decimal( response.json()['bid'] )
    askprice = str( Decimal( bidprice + tick ).quantize( bidprice ) )
    quantity = str( Decimal( notional / Decimal(askprice) ).quantize( tick ) )

    # Update logs.
    logger.debug(f'Bidprice: {bidprice}')
    logger.debug(f'Askprice: {askprice}')
    logger.debug(f'Quantity: {quantity}')

    # Construct buy order payload.
    # Use 'options': ['maker-or-cancel'] for post only orders.
    endpoint = '/v1/order/new'
    t = datetime.datetime.now()
    payload = {
        'request': endpoint,
        'nonce': str( int ( time.mktime( t.timetuple() ) * 1000 ) ),
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
