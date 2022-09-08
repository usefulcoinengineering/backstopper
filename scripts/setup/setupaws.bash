#!/usr/bin/bash
# 
# script name: setupaws.bash
# script author: munair simpson
# script created: 20220804
# script purpose: setup aws credentials for the messenger

mkdir ~/.aws
cat > ~/.aws/config << EOF
[default]
region=us-east-1
EOF
cat > ~/.aws/credentials << EOF
[default]
aws_access_key_id = AKIARB33NP5HGWSP145K
aws_secret_access_key = c/MVoL9wOiKnt4fyPhKRWOt@hqqKhfvLcon!oZJ/
EOF
