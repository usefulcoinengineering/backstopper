#! /bin/bash
#
# script name: messenger.bash
# script author: munair simpson
# script created: 20220819
# script purpose: wrapper for messenger.py

# Send message specified.
# Parameter 0 is the message.

# Execution:
# python3 messenger.py "Sending a test message from a BASH script."

if [ -z "$1" ] ; then
    echo -e "\nNormal usage: \n\tbash messenger.bash 'message' \n\nBut no argument supplied. Let's gather it now... "
    message="\"Sending a test message from a BASH script that is a wrapper around a Python module (messenger.py).\""
    read -p "Type a replacement value or press enter to continue with default argument [$message]: " message && message=${message:-sending_a_test_message_from_a_BASH_script}

else
    message=$1

fi

cd ../../backstopper/messaging/
python3 messenger.py $message