import alpaca_trade_api as tradeapi
import os
from dotenv import load_dotenv
import requests
import json
from datetime import datetime
import numpy as np
import talib
import matplotlib.pyplot as plt

load_dotenv()
API_KEY = os.getenv('API_KEY')
API_SECRET = os.getenv('API_SECRET')
APCA_API_BASE_URL = os.getenv('AAPCA_API_BASE_URL')
MY_WATCHLIST_ID = os.getenv('MY_WATCHLIST_ID')

# or use ENV Vars shown below
api = tradeapi.REST(API_KEY, API_SECRET, api_version='v2')
account = api.get_account()

# print(api.get_watchlist(MY_WATCHLIST_ID))
# print(api.get_position('TWTR'))

# print(account, account.buying_power, account.equity, account.cash)
# print(api.close_all_positions())
# print(api.get_barset('AAPL', "1D", 1)) Day stats of APPL stock


barTimeframe = "15Min"  # 1Min, 5Min, 15Min, 1H, 1D
assetsToDownload = ["TSLA", "MSFT", "AAPL", "AMZN"]
# Start date for the market data in ISO8601 format
startDate = "2019-11-01T09:30:00-04:00"

# Tracks position in list of symbols to download
iteratorPos = 0
assetListLen = len(assetsToDownload)

while iteratorPos < assetListLen:
    symbol = assetsToDownload[iteratorPos]

    returned_data = api.get_barset(symbol, barTimeframe, start=startDate)
    timeList = []
    openList = []
    highList = []
    lowList = []
    closeList = []
    volumeList = []

    # Reads, formats and stores the new bars
    bars = returned_data[symbol]
    for bar in bars:
        timeList.append(bar.t)
        openList.append(bar.o)
        highList.append(bar.h)
        lowList.append(bar.l)
        closeList.append(bar.c)
        volumeList.append(bar.v)

    # Processes all data into numpy arrays for use by talib
    timeList = np.array(timeList)
    openList = np.array(openList, dtype=np.float64)
    highList = np.array(highList, dtype=np.float64)
    lowList = np.array(lowList, dtype=np.float64)
    closeList = np.array(closeList, dtype=np.float64)
    volumeList = np.array(volumeList, dtype=np.float64)

    # Calculated trading indicators
    SMA20 = talib.EMA(closeList, 20)
    SMA50 = talib.EMA(closeList, 50)

    print(SMA50[-1])