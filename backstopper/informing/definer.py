#!/usr/bin/env python3
#
# test name: definer.py
# test author: munair simpson
# test created: 20220812
# test purpose: define constants (like resource locators) used by libraries.


restsandbox = 'https://api.sandbox.gemini.com'
restgenuine = 'https://api.gemini.com'
socksandbox = 'wss://api.sandbox.gemini.com'
sockgenuine = 'wss://api.gemini.com'

# Production Servers:
sockserver = sockgenuine
restserver = restgenuine

# Sandbox Servers
# sockserver = socksandbox
# restserver = restsandbox

# Note:
#
# The source of these constants can be located here:
#  - https://docs.gemini.com/rest-api/#symbols-and-minimums
#
# Unfortunately, they don't always match up with the Gemini web interface and API.
#
# So you can also try here:
#  - https://support.gemini.com/hc/en-us/articles/4401824250267-Are-there-trading-minimums-
#
# The following were manually updated:
#  - YFI TICK : 0.01

apitransactionfee = '0.002'
# apitransactionfee = '0.001' originally

# Manually configured DAI (was '0.000001')
# Manually configured ETH (was '0.000001')
# Manually configured ZRC (was '0.000001')
# Manually configured BTC (was '0.00000001')
# Manually configured ENS (was '0.000001')

ticksizes = [
 {
   'currency': 'BTC',
   'tick': '0.01'
 },
 {
   'currency': 'ETH',
   'tick': '0.01'
 },
 {
   'currency': 'ZEC',
   'tick': '0.000001'
 },
 {
   'currency': 'BCH',
   'tick': '0.000001'
 },
 {
   'currency': 'LTC',
   'tick': '0.00001'
 },
 {
   'currency': 'BAT',
   'tick': '0.000001'
 },
 {
   'currency': 'DAI',
   'tick': '0.00001'
 },
 {
   'currency': 'LINK',
   'tick': '0.000001'
 },
 {
   'currency': 'OXT',
   'tick': '0.000001'
 },
 {
   'currency': 'AMP',
   'tick': '0.000001'
 },
 {
   'currency': 'COMP',
   'tick': '0.000001'
 },
 {
   'currency': 'PAXG',
   'tick': '0.00000001'
 },
 {
   'currency': 'MKR',
   'tick': '0.000001'
 },
 {
   'currency': 'ZRX',
   'tick': '0.00001'
 },
 {
   'currency': 'KNC',
   'tick': '0.000001'
 },
 {
   'currency': 'MANA',
   'tick': '0.000001'
 },
 {
   'currency': 'STORJ',
   'tick': '0.000001'
 },
 {
   'currency': 'SNX',
   'tick': '0.000001'
 },
 {
   'currency': 'CRV',
   'tick': '0.000001'
 },
 {
   'currency': 'BAL',
   'tick': '0.000001'
 },
 {
   'currency': 'UNI',
   'tick': '0.000001'
 },
 {
   'currency': 'REN',
   'tick': '0.000001'
 },
 {
   'currency': 'UMA',
   'tick': '0.000001'
 },
 {
   'currency': 'YFI',
   'tick': '0.01'
 },
 {
   'currency': 'AAVE',
   'tick': '0.000001'
 },
 {
   'currency': 'ENS',
   'tick': '0.001'
 }
]

# DAI Manually Updated (was '0.1')
# ENS Manually Added

minimumorders = [
 {
   'currency': 'BTC',
   'minimumorder': '0.00001'
 },
 {
   'currency': 'ETH',
   'minimumorder': '0.001'
 },
 {
   'currency': 'ZEC',
   'minimumorder': '0.001'
 },
 {
   'currency': 'BCH',
   'minimumorder': '0.001'
 },
 {
   'currency': 'LTC',
   'minimumorder': '0.01'
 },
 {
   'currency': 'BAT',
   'minimumorder': '1.0'
 },
 {
   'currency': 'DAI',
   'minimumorder': '0.00001'
 },
 {
   'currency': 'LINK',
   'minimumorder': '0.1'
 },
 {
   'currency': 'OXT',
   'minimumorder': '1.0'
 },
 {
   'currency': 'AMP',
   'minimumorder': '10.0'
 },
 {
   'currency': 'COMP',
   'minimumorder': '0.001'
 },
 {
   'currency': 'PAXG',
   'minimumorder': '0.0001'
 },
 {
   'currency': 'MKR',
   'minimumorder': '0.001'
 },
 {
   'currency': 'ZRX',
   'minimumorder': '0.1'
 },
 {
   'currency': 'KNC',
   'minimumorder': '0.1'
 },
 {
   'currency': 'MANA',
   'minimumorder': '1.0'
 },
 {
   'currency': 'STORJ',
   'minimumorder': '0.1'
 },
 {
   'currency': 'SNX',
   'minimumorder': '0.01'
 },
 {
   'currency': 'CRV',
   'minimumorder': '0.1'
 },
 {
   'currency': 'BAL',
   'minimumorder': '0.01'
 },
 {
   'currency': 'UNI',
   'minimumorder': '0.01'
 },
 {
   'currency': 'REN',
   'minimumorder': '0.01'
 },
 {
   'currency': 'UMA',
   'minimumorder': '0.01'
 },
 {
   'currency': 'YFI',
   'minimumorder': '0.00001'
 },
 {
   'currency': 'AAVE',
   'minimumorder': '0.001'
 },
 {
   'currency': 'ENS',
   'minimumorder': '0.002'
 }
]

# ETH Manually Updated (was '0.001')
# ENS Manually Added

minimumquantities = [
 {
   'currency': 'BTC',
   'minimumquantity': '0.00001'
 },
 {
   'currency': 'ETH',
   'minimumquantity': '0.000001'
 },
 {
   'currency': 'ZEC',
   'minimumquantity': '0.001'
 },
 {
   'currency': 'BCH',
   'minimumquantity': '0.001'
 },
 {
   'currency': 'LTC',
   'minimumquantity': '0.01'
 },
 {
   'currency': 'BAT',
   'minimumquantity': '1.0'
 },
 {
   'currency': 'DAI',
   'minimumquantity': '0.00001'
 },
 {
   'currency': 'LINK',
   'minimumquantity': '0.1'
 },
 {
   'currency': 'OXT',
   'minimumquantity': '1.0'
 },
 {
   'currency': 'AMP',
   'minimumquantity': '10.0'
 },
 {
   'currency': 'COMP',
   'minimumquantity': '0.001'
 },
 {
   'currency': 'PAXG',
   'minimumquantity': '0.0001'
 },
 {
   'currency': 'MKR',
   'minimumquantity': '0.001'
 },
 {
   'currency': 'ZRX',
   'minimumquantity': '0.1'
 },
 {
   'currency': 'KNC',
   'minimumquantity': '0.1'
 },
 {
   'currency': 'MANA',
   'minimumquantity': '1.0'
 },
 {
   'currency': 'STORJ',
   'minimumquantity': '0.1'
 },
 {
   'currency': 'SNX',
   'minimumquantity': '0.01'
 },
 {
   'currency': 'CRV',
   'minimumquantity': '0.1'
 },
 {
   'currency': 'BAL',
   'minimumquantity': '0.01'
 },
 {
   'currency': 'UNI',
   'minimumquantity': '0.01'
 },
 {
   'currency': 'REN',
   'minimumquantity': '0.01'
 },
 {
   'currency': 'UMA',
   'minimumquantity': '0.01'
 },
 {
   'currency': 'YFI',
   'minimumquantity': '0.00001'
 },
 {
   'currency': 'AAVE',
   'minimumquantity': '0.001'
 },
 {
   'currency': 'ENS',
   'minimumquantity': '0.002'
 }
]
