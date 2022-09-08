#!/usr/bin/bash
# 
# script name: gemini-ethusd-trailer.bash
# script author: munair simpson
# script created: 20220827
# script purpose: start or stop a Gemini ETHUSD trailer bot from [~/bots]
# script argument: the action desired [start/stop]

# step 1: check for bots
ps auwx | grep -e "bash [bf]" -e "python3 \." | grep -v "$0" && echo "There is at least one active bot running. "

# step 2: request directive
read -p "start/stop trading bot [start]: " action
action=${action:-"start"} 

# step 3: execute directive
if [ $action == "stop" ]; then kill -s KILL $(ps auwx | grep -E 'bash [bf]|python3 \.' | awk '{print $2}') ; fi
if [ $action == "start" ]; then cd gemini/strategies/ && git pull && nohup bash frontrunningethusdtrailingstop.bash ; fi

exit 0