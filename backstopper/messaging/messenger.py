#!/usr/bin/env python3
#
# library name: messenger.py
# library author: munair simpson
# library created: 20220819
# library purpose: send alert messages to a monitored Discord Server Channel using webhooks.

import json
from logging import Logger
import requests

from logging import logger as logger

import backstopper.authenticating.credentials as credentials

# Define alert function
def sendmessage( message ):

    try : 

        appresponse = requests.post( credentials.discordwebhook, 
                                     data = json.dumps( { "content": message } ), 
                                     headers = { 'Content-Type': 'application/json' } 
        ) # Send message to Discord server.

    except Exception as e :

        logger.error ( f'Error: {e}' ) # Log error details in case there is an error.
    
    logger.info ( f'Response to Discord Request:\n{appresponse}' ) # Log successful requests to the console.

if __name__ == "__main__":

    import sys

    # Set default message in case a BASH wrapper has not been used.
    message = "Sending a test message from a Python script using this custom messenger.py module."

    # Override defaults with command line parameters from BASH wrapper.
    if len(sys.argv) == 2 : message = sys.argv[1]
    else : logger.warning ( f'Incorrect number of command line arguments. Using default value of {message}...' )

    # Send message.
    sendmessage( message )
