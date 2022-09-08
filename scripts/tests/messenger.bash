#! /bin/bash
#
# script name: messenger.bash
# script author: munair simpson
# script created: 20220819
# script purpose: wrapper for messenger.py

# Send message specified.
# Parameter 0 is the message.

# Execution:
# python3 ../messenger.py "Sending a test message from a BASH script."

message="\"Sending a test message from a BASH script that is a wrapper around a Python module (messenger.py).\""

read -p "type a replacement value or press enter to continue with default argument [$message]: " message && message=${message:-sending_a_test_message_from_a_BASH_script}

python3 ../../backstopper/messaging/messenger.py $message