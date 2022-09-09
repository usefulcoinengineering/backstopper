#!/usr/bin/bash
# 
# script name: backstopper.bash
# script author: munair simpson
# script created: 20220909
# script purpose: start or stop a Gemini backstopper bot
# script argument: the action desired [start/stop]

# check for running bots/processes.
echo -e "\nchecking for active backstopper bots... "
ps auwx | grep -e "backstopper" | grep -v "grep" && echo -e "\t...there are active backstopper bots running.\n "
if [ $? == "1" ]; then echo -e "\t...no active bots found...\n " ; fi

# do we kill existing processes or start a new bot?
action="start" && read -p "start/stop trading bot [$action]: " enteredvalue && action=${enteredvalue:-$action}
if [ $action == "stop" ]; then kill -s KILL $(ps auwx | grep -e "backstopper" | grep -v "grep" | awk '{print $2}') ; fi
if [ $action == "start" ]; then 

    # either use arguments.
    if [ $# == "5" ]; then
        pair=$1
        size=$2
        stop=$3
        sell=$4
    else
        # or confirm/define default values.
        pair="ETHUSD" && read -p "specify asset pair [the default value is $pair]: " enteredvalue && pair=${enteredvalue:-$pair}
        size="0.0010" && read -p "specify trade size [the default value is $size]: " enteredvalue && size=${enteredvalue:-$size}
        stop="0.0010" && read -p "specify price stop [the default value is $stop]: " enteredvalue && stop=${enteredvalue:-$stop}
        sell="0.0010" && read -p "specify price sell [the default value is $sell]: " enteredvalue && sell=${enteredvalue:-$sell}
        echo -e "\ngoing to execute:\n\npython3 -m backstopper $pair $size $stop $sell\n\n"
    fi
    
    # get latest version.
    cd $(find / -type d -name "backstopper" 2>/dev/null | head -1) && git pull

    # execute latest version.
    python3 -m backstopper $pair $size $stop $sell
fi