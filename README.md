# Backstopper

This repository is a collection of packages that engage with a trading account on Gemini to purchase an asset and sell it after the price rises a specified amount. However, the selling price is continually updated if the prices rise further.

## Quickstart

Run the following commands to rapidly setup the execution environment:

```bash
git clone https://github.com/usefulcoinengineering/backstopper.git
cd backstopper
cp backstopper/examples/example-credentials.py backstopper/authenticating/credentials.py
sudo apt-get update --assume-yes
sudo apt-get install --assume-yes python3-pip
pip3 install websockets
sudo timedatectl set-timezone America/Jamaica
bash scripts/sethostname.bash
pip install -e .
```

## Gemini API Credentials:

You need to edit credentials.py and add your real Gemini API credentials.

## Timezone Support:

You may need to change the timezone to your location. For example, if in Los Angeles, California (i.e. PST):

```bash
sudo timedatectl set-timezone America/Los_Angeles
```

This will make it easier to read the logfiles.

## Hostname Configuration:

It helps to name your AWS EC2 instance. To do so run the scripts/sethostname.bash BASH script:

```bash
bash scripts/sethostname.bash
```

## Discord Support:

Edit credentials.py to include the webhook to a monitored Discord Channel:

```bash
discordwebhook = 'https://discord.com/api/webhooks/1006964160514502888/9I0BJ5kReoZ0NPGvwJklrHiivh12_sYe9wSJzht-wyWJJ1ilAMQs7y0TDBxFKpqyt_mO'
```

## Amazon Support:

The libraries no longer use SNS by default because it became very onerous to send messages with AWS. Sending messages 
programmatically to a monitored Discord channel using webhooks is preferred. However, for those with a preference for 
AWS and SNS, follow these instructions:

1. To get SNS support, open up IAM and add a new user that has privileges to send messages (i.e. attach a policy like **AmazonSNSFullAccess** to a user with programmatic AWS access type).
2. Copy the credentials to the EC2 instance (or MacBook Pro) used for trading:

```bash
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
```

or run the scripts/setupaws.bash BASH script with your credentials.

## Monitoring Prices

Use the following command to stream trade information from the Gemini websocket server:

```bash
python3 -m websockets wss://api.gemini.com/v1/marketdata/ethusd?trades=true
```


