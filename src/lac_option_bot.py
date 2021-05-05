# import packages
#import sys
#sys.path.append('/usr/local/lib/python3.7/site-packages')
from tda import auth, client # pip install tda-api
import requests, json
from datetime import datetime, timedelta
import pandas as pd
from config import api_key, token_path, redirect_uri, account_number, alpha_api_key, driver_path
import functions as fn
import sys

# authenticate TD Ameritrade user
try:
    c = auth.client_from_token_file(token_path, api_key)
# if we can't authenticate then we need to go to chrome to do so
except FileNotFoundError:
    from selenium import webdriver
    with webdriver.Chrome(executable_path=driver_path) as driver:
        c = auth.client_from_login_flow(driver, api_key, redirect_uri, token_path)

# check rsi of stock
# we're using Alpha Vantage, the free version allows for 5 requests/min
# and a total of 500/day. Can make one request per minute.
# make a new API key if you're going to make a second request
# in a script.
trading_symbol = 'LAC'
rsi = fn.alpha_vantage_rsi(trading_symbol,'30min','14','close',alpha_api_key)
# get transaction info to ensure we haven't already done the trade
transactions = c.get_transactions(account_id=account_number,symbol=trading_symbol, start_date=datetime.now()+timedelta(days=-7), end_date=datetime.now())
options_trades = fn.td_option_trades(transactions) # gather recent option trades to stop us from entering a second trade

# run account information, define a function in functions.py that will ouput
# everything you need from the account call so we call it only once.
# on_hand, day_trades, etc.

# position entrance
if entrance(rsi,options_trades)==True:

    # get account information
    acct = c.get_account(account_id=account_number, fields=c.Account.Fields.POSITIONS) # get current positions to kick down to check if we should sell
    # acct = acct.json()
    on_hand = acct.json()["securitiesAccount"]["currentBalances"]["availableFunds"]
    # get options chain
    search_range = datetime.now() + timedelta(days=360)
    chain = c.get_option_chain(symbol=trading_symbol,contract_type=c.Options.ContractType.PUT,include_quotes=True,strike_from_date=datetime.now(),strike_to_date=search_range)
    chain = chain.json()
    chain = chain["putExpDateMap"] # options chain, enumerated by the strike price
    expirations = list(chain.keys()) # expirations in the chain
    days_out = []
    option_dict = {}
    for expiration in expirations:
        exp_date, days_away = expiration.split(":")
        option_dict[days_away] = exp_date
        days_away = int(days_away)
        days_out.append(days_away)
    selection = fn.take_closest(30,days_out) # takes the closest date to 30 days away from today
    selection = str(selection)
    selected_exp_date = option_dict[str(selection)]
    option_key = selected_exp_date + ":" + selection
    chain = chain[option_key] # now we have strikes to choose
    strikes = list(chain.keys())
    deltas = []
    strike_dict = {}
    symbol_dict = {}
    for strike in strikes:
        # choose the strike closest to delta -0.4
        symbol_dict[str(chain[strike][0]["delta"])] = chain[strike][0]["symbol"]
        strike_dict[str(chain[strike][0]["delta"])] = strike
        deltas.append(chain[strike][0]["delta"])
    delta_selection = fn.take_closest(-0.4,deltas)
    sell_option_strike_selection = strike_dict[str(delta_selection)] # we use the symbol to execute the trade itself
    sell_option_symbol_selection = symbol_dict[str(delta_selection)]
    # get premium
    premium = chain[sell_option_strike_selection][0]["mark"]*100
    # build the trade logic of whether to place the trade or not
    # we already have: if rsi<30 & day trade hasn't happened yet this week (last 7 days)
    # we should check cash on hand, day trades, and whether we're in the position already or not


# position exit


# not ready to enter
else:
    sys.exit()
