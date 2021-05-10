#Main program w/ websockets

import numpy, talib, math, websocket, json, pprint
from coinbase.wallet.client import Client
from time import sleep
from data import api_key, api_secret #This is just a file with the API keys - intentionally left out of the repo for security reasons
from analytics import percentage_change
from decimal import *

#Setting up Coinbase client
#client = Client(api_key, api_secret)
#payment_method = client.get_payment_methods()[0]

SOCKET = "wss://ws-feed.pro.coinbase.com"

#TA Lib stuff
RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30
TRADE_QUANTITY = Decimal(0.0005)

#How often to update prices (in seconds)
cycle_time = 5
cycle = cycle_time

in_position = False
bought_at = Decimal(0)        #Remember buy-in price
running_total = Decimal(0)    #Total profit/loss
hold_counter = 0

price_list = []

def on_open(ws):
    print("Opened connection")
    subscribe = {
                    "type": "subscribe",
                    "product_id": "BTC-USD",
                    "channels": [{ "name": "ticker", "product_ids": ["BTC-USD"] }]
                }
    subscribe_json = json.dumps(subscribe)
    ws.send(subscribe_json)

def on_close(ws):
    print("Closed connection")

def on_message(ws, message):
    global price_list
    global in_position
    global cycle_time
    global cycle

    json_message = json.loads(message)
    #print("Recieved message: {}".format(json_message))
    #pprint.pprint(json_message)

    current_price = json_message['price']

    if cycle == 0: #TODO: Make this only check price after a given time interval
        cycle = cycle_time
        price_list.append(float(current_price))
        #print("Current price: {}".format(current_price))

        if len(price_list) > RSI_PERIOD:
            np_prices = numpy.array(price_list)
            rsi = talib.RSI(np_prices, RSI_PERIOD)
            last_rsi = rsi[-1]
            print("Current RSI: {}".format(last_rsi))
            #print("In position: {}".format(in_position))

            if last_rsi > RSI_OVERBOUGHT:
                if in_position:
                    print("Sell!")
                    in_position = False
                else:
                    print("Overbought, but nothing to sell.")

            if last_rsi < RSI_OVERSOLD:
                if in_position:
                    print("Oversold, but already in.")
                else:
                    print("Buy!")
                    in_position = True
    else:
        print("Waiting... ({}) ".format(cycle), end = "\r")
        cycle -= 1
        sleep(1)


ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
ws.run_forever()
