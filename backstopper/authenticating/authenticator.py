#!/usr/bin/env python3
#
# library name: authenticator.py
# library author: munair simpson
# library created: 20220816
# library purpose: authenticate payloads for private interations with Gemini API servers.

import json
import base64
import hmac
import hashlib

import backstopper.authenticating.credentials as credentials

def authenticate ( payload ) -> str :
    encodedpayload = json.dumps( payload ).encode()
    b64 = base64.b64encode( encodedpayload )
    signature = hmac.new( credentials.secret.encode(), b64, hashlib.sha384 ).hexdigest()
    apihead = { 'Content-Type': "text/plain",
                'Content-Length': "0",
                'X-GEMINI-APIKEY': credentials.key,
                'X-GEMINI-PAYLOAD': b64,
                'X-GEMINI-SIGNATURE': signature,
                'Cache-Control': "no-cache" }
    wsshead = { 'X-GEMINI-PAYLOAD': b64.decode(),
                'X-GEMINI-APIKEY': credentials.key,
                'X-GEMINI-SIGNATURE': signature }

    return { 'sockheader': wsshead, 'restheader': apihead }
