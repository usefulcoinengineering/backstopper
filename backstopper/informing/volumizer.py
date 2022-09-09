#!/usr/bin/env python3
#
# library name: volumizer.py
# library author: munair simpson
# library created: 20210307
# library purpose: retrieve trading activity dependent data for the last 30 days across all pairs traded


import requests
import datetime
import time

from backstopper.informing.definer import restserver

from backstopper.logging.logger import logger as logger
from backstopper.authenticating.authenticator import authenticate as authenticate

def notionalvolume() -> str:

    # Retrieve activity based data 
    # like transaction fees and 
    # trading volume (USD terms).
    endpoint = '/v1/notionalvolume'
    t = datetime.datetime.now()
    payload = {
        'nonce': str( int( time.mktime( t.timetuple() ) * 1000 ) ),
        'request': endpoint
    }
    headers = authenticate( payload )

    request = restserver + endpoint
    response = requests.post( request, data = None, headers = headers['restheader'] )

    return response

if __name__ == "__main__":

    notionalvolume()