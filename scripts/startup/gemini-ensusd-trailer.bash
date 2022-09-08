#!/usr/bin/bash
# 
# script name: gemini-ensusd-trailer.bash
# script author: munair simpson
# script created: 20220827
# script purpose: start or stop a Gemini ENSUSD trailer bot from [~/bots]
# script argument: the action desired [start/stop]

echo "checking for active bots... "
ps auwx | grep -e "bash [bf]" -e "python3 \." | grep -v "gemini-ensusd-trailer.bash" && echo "there are active bots running. "
if [ $? == "1" ]; then echo "no active bots found... " ; fi

read -p "start/stop trading bot [start]: " action
action=${action:-start}

if [ $action == "stop" ]; then kill -s KILL $(ps auwx | grep -E 'bash [bf]|python3 \.' | awk '{print $2}') ; fi
if [ $action == "start" ]; then cd gemini/strategies/ && git pull && nohup bash frontrunningensusdtrailingstop.bash ; fi