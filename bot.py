#Main program

import numpy, talib, math
from coinbase.wallet.client import Client
from time import sleep
from data import api_key, api_secret #This is just a file with the API keys - intentionally left out of the repo for security reasons
from analytics import percentage_change
from decimal import *

#Setting up Coinbase client
client = Client(api_key, api_secret)
#payment_method = client.get_payment_methods()[0]

#Take user input
#user_limit_order = float(input("Enter a price for your Bitcoin limit order (USD): "))
#user_amount_spent = float(input("Enter how much you want to spend (USD): "))

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

def buyBtc(quantity, price):
    try:
        bought_at = Decimal(quantity) * Decimal(price)
        #running_total -= float(quantity) * float(price)
        bTxt ="Bought {:.6f} BTC at ${:,.2f}/BTC for a total of ${:,.2f}"
        print(bTxt.format(Decimal(quantity), Decimal(price), Decimal(quantity) * Decimal(price)))
    except Exception as e:
        print("Error within buyBtc")
        print(e)
        return False
    return True

def sellBtc(quantity, price):
    try:
        #running_total += float(quantity) * float(price)
        sTxt = "Sold {:.6f} BTC at ${:,.2f}/BTC for a total of ${:,.2f}"
        print(sTxt.format(Decimal(quantity), Decimal(price), Decimal(quantity) * Decimal(price)))
    except Exception as e:
        print("Error within sellBtc")
        print(e)
        return False
    return True

while(True):

    buy_price = client.get_buy_price(currency=currency_code)
    sell_price = client.get_sell_price(currency=currency_code)
    spot_price = client.get_spot_price(currency=currency_code)
    percentage_gainloss = percentage_change(start_price.amount, buy_price.amount)
    changes_list.append(float(spot_price.amount))

    #Trading debug
    '''
    if in_position:
        test_sell = sellBtc(TRADE_QUANTITY, sell_price.amount)
        if test_sell:
            running_total += Decimal(TRADE_QUANTITY) * Decimal(buy_price.amount)
            #print(running_total)
            print("Running total of gain/loss: ${:,.2f}".format(running_total.quantize(Decimal('.01'), rounding=ROUND_HALF_UP)))
            in_position = False
    else:
        test_buy = buyBtc(TRADE_QUANTITY, buy_price.amount)
        if test_buy:
            running_total -= Decimal(TRADE_QUANTITY) * Decimal(buy_price.amount)
            #print(running_total)
            print("Running total of gain/loss: ${:,.2f}".format(running_total.quantize(Decimal('.01'), rounding=ROUND_HALF_UP)))
            in_position = True
    '''

    if len(changes_list) > RSI_PERIOD:
        np_closes = numpy.array(changes_list)
        rsi = talib.RSI(np_closes, RSI_PERIOD)
        '''
        print("All RSIs calculated so far:")
        print(rsi)
        '''
        last_rsi = rsi[-1]
        print("Current profit/loss:\t${:,.2f}\nCurrent rsi:\t{:.2f}".format(running_total,float(last_rsi)))

        if last_rsi > RSI_OVERBOUGHT:
            if in_position and (((Decimal(sell_price.amount) * TRADE_QUANTITY).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)) > Decimal(bought_at).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)):
                print("Sell!")
                print((Decimal(sell_price.amount) * TRADE_QUANTITY).quantize(Decimal('.01'), rounding=ROUND_HALF_UP))
                print("is greater than price bought at:")
                print(Decimal(bought_at).quantize(Decimal('.01'), rounding=ROUND_HALF_UP))
                sell_succeeded = sellBtc(TRADE_QUANTITY, sell_price.amount)
                if sell_succeeded:
                    running_total += Decimal(TRADE_QUANTITY) * Decimal(sell_price.amount)
                    print("Running total of gain/loss: ${:,.2f}".format(round(running_total, 2)))
                    in_position = False
            elif in_position and (((Decimal(sell_price.amount) * TRADE_QUANTITY).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)) <= Decimal(bought_at).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)):
                if hold_counter == 5:
                    hold_counter = 0
                    print("Overbought - selling despite loss due to hold timer")
                    sell_succeeded = sellBtc(TRADE_QUANTITY, sell_price.amount)
                    if sell_succeeded:
                        running_total += Decimal(TRADE_QUANTITY) * Decimal(sell_price.amount)
                        print("Running total of gain/loss: ${:,.2f}".format(round(running_total, 2)))
                        in_position = False
                else:
                    hold_counter += 1
                    print("Overbought, but selling would cause a loss. Count: {}".format(hold_counter))
            else:
                print("Overbought, but nothing to sell")

        if last_rsi < RSI_OVERSOLD:
            hold_counter = 0
            if in_position:
                print("Oversold, but already own it")
            else:
                print("Buy!")
                buy_succeeded = buyBtc(TRADE_QUANTITY, buy_price.amount)
                if buy_succeeded:
                    running_total -= Decimal(TRADE_QUANTITY) * Decimal(buy_price.amount)
                    print("Running total of gain/loss: ${:,.2f}".format(round(running_total, 2)))
                    in_position = True
    
    #Print current BTC price + percent change
    print('Bitcoin is ${:,.2f} \nPercent change in last {} seconds: {:.3f}%\n'.format(float(buy_price.amount), CYCLE_TIME, percentage_gainloss))
    '''
    #Sell, if within sell threshold
    if(float(sell_price.amount) > user_limit_order):
        btc_amount_sold = 0
        #sell = ''
        sTxt = "Sold {:.6f} BTC at ${:,.2f}/BTC for a total of ${:,.2f}" 
        print(sTxt.format(float(btc_amount_sold), float(sell_price.amount), float(btc_amount_sold * float(sell_price.amount))))

    #Buy, if within purchase threshold
    elif(float(buy_price.amount) <= user_limit_order):

        #buy = client.buy(amount=str(user_amount_spent / float(buy_price.amount), currency=currency_code, payment_method=payment_method.id))

        #print("Bought $" + str(user_amount_spent) + " or " + str(user_amount_spent / float(buy_price.amount)) + " bitcoin at " + buy_price.amount)
        bTxt ="Bought {:.6f} BTC at ${:,.2f}/BTC for a total of ${:,.2f}"
        print(bTxt.format(float(user_amount_spent / float(buy_price.amount)),float(buy_price.amount), user_amount_spent))

    #Do nothing/hold
    else:
        print("Holding...")
    '''
    #Sleep
    for i in range(CYCLE_TIME, 0, -1):
        print("Waiting... ({}) ".format(i), end = "\r")
        sleep(1)

    #Update start_price
    start_price = buy_price