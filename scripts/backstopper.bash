#!/usr/bin/bash
# 
# script name: backstopper.bash
# script author: munair simpson
# script created: 20220909
# script purpose: start or stop a Gemini backstopper bot
# script argument: the action desired [start/stop]

echo -e "\nchecking for active bots... "
ps auwx | grep -e "backstopper" | grep -v "grep" && echo -e "\tthere are active bots running. "
if [ $? == "1" ]; then echo -e "\tno active bots found... " ; fi

read -p "start/stop trading bot [start]: " action
action=${action:-start}

if [ $action == "stop" ]; then kill -s KILL $(ps auwx | grep -e "backstopper" | grep -v "grep" | awk '{print $2}') ; fi
if [ $action == "start" ]; then 
    pair='ETHUSD'
    size='0.0010'
    stop='0.0010'
    sell='0.0010'
    cd $(find / -type d -name "backstopper" 2>/dev/null | head -1)
    git pull
    python3 -m backstopper $pair $size $stop $sell
fi