#Main program

import numpy, talib, math, websocket, json
from coinbase.wallet.client import Client
from time import sleep
from data import api_key, api_secret #This is just a file with the API keys - intentionally left out of the repo for security reasons
from analytics import percentage_change
from decimal import *

#Setting up Coinbase client
client = Client(api_key, api_secret)
#payment_method = client.get_payment_methods()[0]

SOCKET = "wss://ws-feed.pro.coinbase.com"

def on_open(ws):
    print("Opened connection")
    subscribe = {
                    "type": "subscribe",
                    "product_id": "BTC-USD",
                    "channels": [{ "name": "heartbeat", "product_ids": ["BTC-USD"] }]
                }
    subscribe_json = json.dumps(subscribe)
    ws.send(subscribe_json)

def on_close(ws):
    print("Closed connection")

def on_message(ws, message):
    json_message = json.loads(message)
    print("Recieved message: {}".format(json_message))    

ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
ws.run_forever()


currency_code = 'USD'

start_price = client.get_buy_price(currency=currency_code)

#How often to update prices (in seconds)
CYCLE_TIME = 20

#TA Lib stuff
RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30
TRADE_QUANTITY = Decimal(0.0005)

changes_list = []
in_position = False
bought_at = Decimal(0)        #Remember buy-in price
running_total = Decimal(0)    #Total profit/loss
hold_counter = 0
