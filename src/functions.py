from tda import auth, client # pip install tda-api
import requests, json
from datetime import datetime, timedelta
import pandas as pd
from config import api_key, token_path, redirect_uri, account_number, alpha_api_key, driver_path
import functions as fn

# position entrance checker
def entrance(rsi,options_trades):
   if rsi>30 and 'LAC' not in options_trades:
      return(True)
# find closest value in a collection to the given num
def take_closest(num,collection):
   return min(collection,key=lambda x:abs(x-num))

# return the rsi of a given instrument, et al.
def alpha_vantage_rsi(trading_symbol,interval,time_period,series_type,alpha_api_key):
   r = requests.get('https://www.alphavantage.co/query?function=RSI&symbol={}&interval={}&time_period={}&series_type={}&apikey={}'.format(trading_symbol, interval, time_period, series_type, alpha_api_key))
   rsi = list(r.json()["Technical Analysis: RSI"].values()) # most recent observation
   return(pd.to_numeric(rsi[0]["RSI"])) # most recent observation

# parse options trades to see if we are currently in the intended option position
def td_option_trades(transactions):
    transactions = transactions.json()
    options_trades = []
    for transaction in transactions:
       if transaction["transactionItem"]["instrument"]["assetType"]=='OPTIONS':
          options_trades.append(transaction["transactionItem"]["instrument"]["symbol"])
    return(options_trades)

 # build a function for operating a wheel strategy with RSI
 # we can build on this in the future to support more entrance
 # types but this is a good place to start
 # def write_put_rsi(c,trading_symbol,rsi,account_number,alpha_api_key,premium_target):
 #    rsi = fn.alpha_vantage_rsi(trading_symbol,'30min','14','close',alpha_api_key)
 #    # get transaction info to ensure we haven't already done the trade
 #    transactions = c.get_transactions(account_id=account_number,symbol=trading_symbol, start_date=datetime.now()+timedelta(days=-7), end_date=datetime.now())
 #    options_trades = fn.td_option_trades(transactions) # gather recent option trades to stop us from entering a second trade
