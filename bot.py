#Main program

from coinbase.wallet.client import Client
from time import sleep
from data import api_key, api_secret #This is just a file with the API keys - intentionally left out of the repo for security reasons
from analytics import percentage_change

#Setting up Coinbase client
client = Client(api_key, api_secret)
#payment_method = client.get_payment_methods()[0]

#Take user input
user_limit_order = float(input("Enter a price for your Bitcoin limit order (USD): "))
user_amount_spent = float(input("Enter how much you want to spend (USD): "))

currency_code = 'USD'

start_price = client.get_buy_price(currency=currency_code)

#How often to update prices (in seconds)
cycle_time = 15

while(True):

    buy_price = client.get_buy_price(currency=currency_code)
    sell_price = client.get_sell_price(currency=currency_code)
    #spot_price = client.get_spot_price(currency=currency_code)
    percentage_gainloss = percentage_change(start_price.amount, buy_price.amount)

    #Print current BTC price + percent change
    print('Bitcoin is ${:.2f} \nPercent change in last {} seconds: {:.6f}%'.format(float(buy_price.amount), cycle_time, percentage_gainloss))

    #Sell, if within sell threshold
    if(float(sell_price.amount) > user_limit_order):
        btc_amount_sold = 0
#        sell = ''
        sTxt = "Sold {:.6f} BTC at ${:.2f}/BTC for a total of ${:.2f}" 
        print(sTxt.format(float(btc_amount_sold), float(sell_price.amount), float(btc_amount_sold * float(sell_price.amount))))

    #Buy, if within purchase threshold
    elif(float(buy_price.amount) <= user_limit_order):

#        buy = client.buy(amount=str(user_amount_spent / float(buy_price.amount), currency=currency_code, payment_method=payment_method.id))

        #print("Bought $" + str(user_amount_spent) + " or " + str(user_amount_spent / float(buy_price.amount)) + " bitcoin at " + buy_price.amount)
        bTxt ="Bought {:.6f} BTC at ${:.2f}/BTC for a total of ${:.2f}"
        print(bTxt.format(float(user_amount_spent / float(buy_price.amount)),float(buy_price.amount), user_amount_spent))

    #Do nothing/hold
    else:
        print("Holding...")
    
    #Sleep
    for i in range(cycle_time, 0, -1):
        print("Waiting... ({})".format(i), end = "\r")
        sleep(1)

    #Update start_price
    start_price = buy_price