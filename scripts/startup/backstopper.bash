#!/usr/bin/bash
# 
# script name: backstopper.bash
# script author: munair simpson
# script created: 20220909
# script purpose: start or stop a Gemini backstopper bot
# script argument: the action desired [start/stop]

echo "checking for active bots... "
ps auwx | grep -e "bash [b]" -e "python3 \." | grep -v "backstopper.bash" && echo "there are active bots running. "
if [ $? == "1" ]; then echo "no active bots found... " ; fi

read -p "start/stop trading bot [start]: " action
action=${action:-start}

if [ $action == "stop" ]; then kill -s KILL $(ps auwx | grep -E 'bash [b]|python3 \.' | awk '{print $2}') ; fi
if [ $action == "start" ]; then 
    pair='ETHUSD'
    size='0.0001'
    stop='0.0100'
    sell='0.0200'
    cd ../.. && pwd && git pull && python3 -m backstopper $pair $size $stop $sell
fi