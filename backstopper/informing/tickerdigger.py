#!/usr/bin/env python3
#
# library name: pricegetter.py
# library author: munair simpson
# library created: 20220811
# library purpose: retrieve market data using the Gemini REST API.

import requests

from backstopper.logging.logger import logger as logger
from backstopper.informing.definer import definer as definer
from backstopper.messaging.messenger import sendmessage as sendmessage

def ticker ( pair : str ) -> str:

    # Get the latest prices and trading volumes.
    endpoint = '/v1/pubticker/' + pair
    response = requests.get( definer.restserver + endpoint ).json()

    # Uncomment to write the response to logs: 
    # logger.debug ( json.dumps( response, sort_keys=True, indent=4, separators=(',', ': ') ) )
 
    return response

if __name__ == "__main__":

    import sys

    # Set default pair in case a BASH wrapper has not been used.
    tradingpair = "ETHUSD"

    # Override defaults with command line parameters from BASH wrapper.
    if len(sys.argv) == 2 : tradingpair = sys.argv[1]
    else : logger.warning ( f'Incorrect number of command line arguments. Using default value of {tradingpair}...' )

    ticker ( tradingpair )