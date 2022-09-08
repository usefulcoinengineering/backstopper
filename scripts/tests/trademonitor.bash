#! /bin/bash
#
# script name: trademonitor.bash
# script author: munair simpson
# script created: 20220831
# script purpose: wrapper for trademonitor.py

# Use websockets to continually monitor the trading range of a trading pair.
# Parameter 0 is the market/trading pair monitored.
# Parameter 1 is the upper price bound that must be breached to exit the price monitor loop.
# Parameter 2 is the lower price bound that must be breached to exit the price monitor loop.

# Execution:
# python3 ../trademonitor.py ETHUSD 1500 1400

marketpair="ETHUSD"
upperbound="1500"
lowerbound="1400"

read -p "type (market/trading) pair or press enter to continue with default [$marketpair]: " marketpair
read -p "type upper price bound or press enter to continue with default [$upperbound]: " upperbound
read -p "type lower price bound or press enter to continue with default [$lowerbound]: " lowerbound

marketpair=${marketpair:-ETHUSD}
upperbound=${upperbound:-1500}
lowerbound=${lowerbound:-1400}

cd ../..
python3 backstopper/monitoring/trademonitor.py $marketpair $upperbound $lowerbound