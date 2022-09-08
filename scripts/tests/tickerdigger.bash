#! /bin/bash
#
# script name: ticker.bash
# script author: munair simpson
# script created: 20220811
# script purpose: wrapper for ticker.py

# Retrieve public market data on the highest bid in the pairbook using Gemini's REST API:
# Parameter 0 is the pair.

# Execution:
# python3 ../ticker.py ENSUSD

pair="ETHUSD"

read -p "type a replacement value or press enter to continue with default argument [$pair]: " pair && pair=${pair:-ETHUSD}

cd ../..
python3 backstopper/informing/tickerdigger.py $pair