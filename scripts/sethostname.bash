#!/usr/bin/bash
# 
# script name: sethostname.bash
# script author: munair simpson
# script created: 20220817
# script purpose: setup instance hostname
# script argument: the server name desired [optional because of default value]

webserver="gemini-trading-bot"

read -p "type hostname or press enter to continue with default [$webserver]: " webserver
webserver=${webserver:-gemini-trading-bot}

sudo hostnamectl set-hostname ${webserver}.localdomain
sudo sed -i "s/127.0.0.1 localhost/127.0.0.1 $webserver.localdomain $webserver localhost4 localhost4.localdomain4/g" /etc/hosts
sudo reboot
