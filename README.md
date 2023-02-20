# webhook-trade-bot
# A simple webhook triggered buy/sell bot running on AWS Flask with python chalice.
# Uses the alpaca-trade-api python lib to push orders.
# Default is paper trade. If you want to do real just change the endpoint.
# Set your maximum balance and the allowance you want for trades inside __init__
# Also remember to set a TV_Key to authenticate your tradingview requests.

Install:
---
conda update conda
conda create -n alert-bot python=3.9
conda activate alert-bot
python -m pip install chalice alpaca-trade-api

Test:
---
# cd to project directory
chalice local
# This will run a local chalice on http://localhost:8000
# Send requests with the following template to http://localhost:8000/sprtrnd
# Below is what you would send from tradingview. Just create an alert and paste
# template in the alert message. Remember the TV_KEY you created or the requests will return an empty list.
# It would be preferable set to return an error.

# random values testing example with insomnia:
{"TVkey": "YourTVKey", "asset_type": "crypto", "action": "sell", "open": 222, "high": 233, "low": 210, "close": 1706, "exchange": "CBSE", "ticker": "ETHUSD", "volume": 11524, "time": "1830", "timenow": "1831"}


# Run:
# create AWS account if you dont have one
# set IAM policy for lambda, get keys
# set keys in /.aws/config
# windows : C:\Users\username\.aws\config
# Then inside project directory to upload the lambda
chalice deploy

# get the url and append /sprtrnd
# Paste it in the alert webhook notification field.
# Add template to alert message

Tradingview Webhook alert template:
{
    "TVkey": "SomeKeyToAuthenticate",
    "asset_type": "crypto",
    #           OR "stock"
    "action": "buy",
    "open": {{open}},
    "high": {{high}},
    "low": {{low}},
    "close": {{close}},
    "exchange": "{{exchange}}",
    "ticker": "{{ticker}}",
    "volume": {{volume}},
    "time": "{{time}}",
    "timenow": "{{timenow}}"
}
