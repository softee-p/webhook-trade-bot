from alpaca_trade_api.rest import REST, TimeFrame
from chalice import Chalice
import requests, json
from math import floor
from chalicelib import *

app = Chalice(app_name='webhook-trade-bot')

# -------------------------------------------#
BASE_URL = "https://paper-api.alpaca.markets"
ACCOUNT_URL = "{}/v2/account".format(BASE_URL)
ORDERS_URL = "{}/v2/orders".format(BASE_URL)
HEADERS = {'APCA-API-KEY-ID': API_KEY, 'APCA-API-SECRET-KEY': SECRET_KEY}

api = REST(key_id=API_KEY,secret_key=SECRET_KEY,base_url=BASE_URL)


def accounting():
    global ALLOWANCE
    account = api.get_account()
    new = float(account.non_marginable_buying_power[0:8])
    diff = BALANCE - new
    if diff < 0:
        ALLOWANCE = ALLOWANCE + diff * -1
    elif diff > 0:
        ALLOWANCE = ALLOWANCE - diff
    else: 
        ALLOWANCE = ALLOWANCE
    print("Check_Pos: ", "allowance is", ALLOWANCE)

# -----get single ticker OR empty for all------ #
def get_positions(ticker=None):
    pos = api.list_positions()
    if ticker != None:
        results = []
        for p in pos:
            if p.symbol == ticker:
                results.append(p)
        if len(results) == 0:
            return 0
        else:
            return results
    if len(pos) == 0:
        return 0
    else:
        return pos

#-                  STRATEGIES                    -#
#----------Supertrend BUY/SELL market order--------#
@app.route('/sprtrnd', methods=['POST'])
def sprtrnd():
    request = app.current_request
    webhook_message = request.json_body
    action = webhook_message["action"]
    asset = webhook_message["asset_type"]
    #-               -Auth-                 -#
    if webhook_message['TVkey'] != TV_KEY:
        return []
    #-             -CheckPos-               -#
    pos = get_positions(webhook_message['ticker'])
    if action == "sell":
        if pos == 0:
            print("ABORTED: no position to sell")
            return []
        # qty is str
        qty = pos[0].qty
    elif action == "buy":
        if pos != 0:
            print("ABORTED: already active position")
            return []
        accounting()
        tmp = str(ALLOWANCE - ALLOWANCE * 0.01)[0:7]
        qty = str(float(tmp) / webhook_message['close'])[0:10]
        if asset == "stock":
            qty = floor(qty)
        
    

    #-        -Alpaca order details-        -#
    print("BALANCE: ", BALANCE)
    print("Set {} market order for qty: {} of {} at ~{} ".format(action, qty, webhook_message['ticker'], webhook_message["close"]))
    data = {
        "symbol": webhook_message['ticker'],
        "qty": qty,
        "side": action,
        "type": "market",
        "time_in_force": "gtc",
    }

    #-           -Post Order-               -#
    r = requests.post(ORDERS_URL, json=data, headers=HEADERS)
    response = json.loads(r.content)
    return {
        'message': "Set SuperTrends {} market order for qty: {} of {} at ~{} ".format(action, qty, webhook_message['ticker'], webhook_message["close"]),
        'webhook_message': webhook_message,
        'response': response
        # 'id': response['id'],
        # 'client_order_id': response['client_order_id']
    }












#-----Bracket Order. Takes only a single buy signal----#
@app.route('/bracket', methods=['POST'])
def bracket():
    request = app.current_request
    webhook_message = request.json_body
    asset = webhook_message["asset_type"]
    #-                -Auth-                          -#
    if webhook_message['TVkey'] != TV_KEY:
        return []
    #-              -CheckPos-                        -#
    pos = get_positions(webhook_message['ticker'])
    action = webhook_message['action']
    if action == "sell":
        if pos == 0:
            print("ABORTED: no position to sell")
            return []
        # qty is str
        qty = pos[0].qty
    elif action == "buy":
        if pos != 0:
            print("ABORTED: already active position")
            return []
        accounting()
        tmp = str(ALLOWANCE - ALLOWANCE * 0.01)[0:7]
        qty = str(float(tmp) / webhook_message['close'])[0:10]
        if asset == "stock":
            qty = floor(qty)

    #-        -Alpaca order details-                  -#
    data = {
        "symbol": webhook_message['ticker'],
        "qty": qty,
        # "side": webhook_message['action'],
        "type": "limit",
        "limit_price": webhook_message['close'],
        "time_in_force": "gtc",
        "order_class": "bracket",
        "take_profit": {
            "limit_price": webhook_message['close'] * 1.05
        },
        "stop_loss": {
            "stop_price": webhook_message['close'] * 0.98,
        }
    }
    #-             -Post Order-                       -#
    r = requests.post(ORDERS_URL, json=data, headers=HEADERS)
    response = json.loads(r.content)
    return {
        'message': 'Set bracket order.',
        'webhook_message': webhook_message,
        'response': response
    }
