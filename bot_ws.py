#Main program w/ websockets

import numpy, talib, math, websocket, json, pprint
from coinbase.wallet.client import Client
from time import sleep
from data import api_key, api_secret #This is just a file with the API keys - intentionally left out of the repo for security reasons
from decimal import *

#Setting up Coinbase client
#client = Client(api_key, api_secret)
#payment_method = client.get_payment_methods()[0]

SOCKET = "wss://ws-feed.pro.coinbase.com"

#How long should we hold for before giving up on profit?
HOLD_MAX = 10

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
bought_at = Decimal(0)
sold_at = Decimal(0)
profit = Decimal(0)

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
    global price_list, in_position, cycle_time, cycle, bought_at, sold_at, profit, hold_counter, HOLD_MAX

    json_message = json.loads(message)
    #print("Recieved message: {}".format(json_message))
    #pprint.pprint(json_message)

    current_price = json_message['price']

    if cycle == 0: #TODO: Make this only check price after a given time interval, instead of just checking once per X messages
        cycle = cycle_time
        price_list.append(float(current_price))
        #print("Current price: {}".format(current_price))

        if len(price_list) > RSI_PERIOD:
            np_prices = numpy.array(price_list)
            rsi = talib.RSI(np_prices, RSI_PERIOD)
            last_rsi = rsi[-1]
            print("Current RSI: {:.2f}".format(last_rsi))
            #print("In position: {}".format(in_position))

            if last_rsi > RSI_OVERBOUGHT:
                if in_position:
                    print("Should we sell?")
                    sold_at = Decimal(price_list[-1])
                    try:
                        if (sold_at * Decimal(0.97)) > bought_at: #Sell if we make a profit including fees
                            print("Selling {:.4f} BTC at ${:,.2f}/BTC for a total of ${:,.2f}".format(TRADE_QUANTITY, sold_at, sold_at * TRADE_QUANTITY))
                            profit += (sold_at - bought_at) * TRADE_QUANTITY
                            print("Profit from this trade: ${:,.2f}\nTotal profit: ${:,.2f}".format((sold_at - bought_at) * TRADE_QUANTITY, profit))
                            in_position = False
                        elif hold_counter == HOLD_MAX:
                            print("Hold limit reached!")
                            hold_counter = 0
                            print("Selling {:.4f} BTC at ${:,.2f}/BTC for a total of ${:,.2f}".format(TRADE_QUANTITY, sold_at, sold_at * TRADE_QUANTITY))
                            profit += (sold_at - bought_at) * TRADE_QUANTITY
                            print("Profit from this trade: ${:,.2f}\nTotal profit: ${:,.2f}".format((sold_at - bought_at) * TRADE_QUANTITY, profit))
                            in_position = False
                        else:
                            print("Don't sell! Hold count: {}".format(hold_counter))
                            hold_counter += 1
                    except Exception as e:
                        print("Exception within overbought: {}".format(e))
                else:
                    print("Overbought, but nothing to sell.")

            if last_rsi < RSI_OVERSOLD:
                hold_counter = 0
                if in_position:
                    print("Oversold, but already in.")
                else:
                    print("Buy!")
                    try:
                        bought_at = Decimal(price_list[-1])
                        print("Bought {:.4f} BTC at ${:,.2f}/BTC for a total of ${:,.2f}".format(TRADE_QUANTITY, bought_at, bought_at * TRADE_QUANTITY))
                        in_position = True
                    except Exception as e:
                        print("Exception within oversold: {}".format(e))
    else:
        print("Waiting... ({}) ".format(cycle), end = "\r")
        cycle -= 1
        #sleep(1)


ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
ws.run_forever()
