#import coinbase
from coinbase.wallet.client import Client
from time import sleep
from data import percentage_change, api_key, api_secret


#Setting up Coinbase client
client = Client(api_key, api_secret)
#payment_method = client.get_payment_methods()[0]

#Take user input
user_limit_order = float(input("Enter a price for your Bitcoin limit order (USD): "))
user_amount_spent = float(input("Enter how much you want to spend (USD): "))

currency_code = 'USD'

start_price = client.get_spot_price(currency=currency_code)

while(True):

    buy_price = client.get_buy_price(currency=currency_code)
    sell_price = client.get_sell_price(currency=currency_code)
    percentage_gainloss = percentage_change(start_price.amount, buy_price.amount)

    #Print current BTC price + percent change
    print('Bitcoin is $' + str(buy_price.amount) + '\nPercent change in last 60 seconds: ' + format(percentage_gainloss, ".3f") + '%')

    #Sell, if within sell threshold
    if(float(buy_price.amount) > user_limit_order):
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
    for i in range(60, 0, -1):
        print("Waiting... ({})".format(i), end = "\r")
        sleep(1)

    #Update start_price
    start_price = buy_price