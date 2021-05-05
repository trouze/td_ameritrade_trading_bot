import sys
sys.path.append('/usr/local/lib/python3.7/site-packages')
from tda import auth, client
import requests
#from datetime import datetime
import json
from config import api_key, token_path, redirect_uri, account_number, fn_api_key
# attempt to authenticate with token file
try:
    c = auth.client_from_token_file(token_path, api_key)
# if we can't authenticate then we need to go to chrome to do so
except FileNotFoundError:
    from selenium import webdriver
    with webdriver.Chrome(executable_path='/Users/trouze/Documents/td_bot/chromedriver') as driver:
        c = auth.client_from_login_flow(
            driver, api_key, redirect_uri, token_path)
# logged in - now we will request stock data on a ticker
r = c.get_quote("LAC").json() # pull current quote on stock
# check the price - if it's good then we'll go ahead and place an order

r_data = r["LAC"] # if we have many tickers, we can run a loop through each but for now we'll just pull the only one
r_acct = c.get_account(account_id=account_number, fields=c.Account.Fields.POSITIONS) # pull current account positions
r_acct = r_acct.json()
r_pos = r_acct["securitiesAccount"]["positions"]
on_hand = r_acct["securitiesAccount"]["currentBalances"]["cashAvailableForTrading"]
pos = []
for symbol in r_pos:
    int = symbol["instrument"]["symbol"]
    pos.append(int) # capture the symbols of the positions we are in

if r_data["bidPrice"]>10 and r_acct["securitiesAccount"]["isDayTrader"]==False and 'LAC' in pos:
    # if ask is below $12 then we're going to place an order
    from tda.orders.equities import equity_sell_market
    ord = c.place_order(account_number, equity_sell_market("LAC",2))
    print(ord)
    sys.exit()
else:
    print('requirements not met to enter position')
    sys.exit()

## unix time
## using finnhub.io for techincal data feed
#import finnhub
#fn_api_key = "bupk44v48v6tm7o42idg"
#fc = finnhub.Client(api_key=fn_api_key)
#print(fc.technical_indicator(symbol="AAPL", resolution='1', _from=ts2, to=ts1, indicator='rsi'))
#import time

#import math
#ts1 = 1605636000
#ts1 = time.time()
#ts1 = math.floor(ts1)
#ts2 = ts1-60

#print(datetime.utcfromtimestamp(ts1).strftime('%Y-%m-%d %H:%M:%S'))
#r = requests.get('https://finnhub.io/api/v1/indicator?symbol=AAPL&resolution=60&from={}&to={}&indicator=rsi&timeperiod=1&token={}'.format(t-60,t,fn_api_key))
#r = r.json()
r = requests.get('https://finnhub.io/api/v1/indicator?symbol=AAPL&resolution=1&from={}&to={}&indicator=rsi&timeperiod=14&token={}'.format(t-840,t,fn_api_key))
