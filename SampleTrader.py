import alpaca_trade_api as tradeapi
import os
from dotenv import load_dotenv
import requests
import json
import time
from pytz import timezone
import datetime
import numpy as np
import ta
import matplotlib.pyplot as plt
from src.Strategies.Helpers.Market import Market
from src.Strategies.Helpers.Account import Account
import pandas as pd

load_dotenv()
API_KEY = os.getenv('API_KEY')
API_SECRET = os.getenv('API_SECRET')
APCA_API_BASE_URL = os.getenv('AAPCA_API_BASE_URL')
MY_WATCHLIST_ID = os.getenv('MY_WATCHLIST_ID')

# or use ENV Vars shown below
api = tradeapi.REST(API_KEY, API_SECRET, api_version='v2')
account = Account(api)
print(account.getEquity())
print(account.getCash())
print(account.getLastEquity())
market = Market(account)
positions = account.getPositions()

print(account.getWatchlists())
