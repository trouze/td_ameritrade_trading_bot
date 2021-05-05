import sys
sys.path.append('/usr/local/lib/python3.7/site-packages')
from tda import auth, client
import json
from config import api_key, token_path, redirect_uri, account_number

try:
    c = auth.client_from_token_file(token_path, api_key)
except FileNotFoundError:
    from selenium import webdriver
    with webdriver.Chrome(executable_path='/Users/trouze/Desktop/td_bot/chromedriver') as driver:
        c = auth.client_from_login_flow(
            driver, api_key, redirect_uri, token_path)

r = c.get_account(account_id=account_number, fields=c.Account.Fields.POSITIONS) # pull current account positions


assert r.status_code == 200, r.raise_for_status()
print(json.dumps(r.json(), indent=4))
