import pandas as pd
import ta
import datetime
from pytz import timezone
import numpy as np
from .Helpers.Stocks import Stocks
from .Helpers.Market import Market
from .Helpers.Account import Account

class MovingAverageStrategy:
    def __init__(self, tradingApi):
        eastern = timezone('US/Eastern')
        today = datetime.datetime.now()
        daystart = eastern.normalize(datetime.datetime(year=today.year, month=today.month,
                            day=today.day, hour=0, second=0, tzinfo=eastern))

        self.Account = Account(tradingApi)
        self.Market = Market(self.Account)
        self.stock_list = ['TSLA'] # Stocks().getStocks()
        self.barTimeframe = "1Min"  # 1Min, 5Min, 15Min, 1H, 1D
        self.startDate = str(daystart.isoformat())
        print(self.startDate)
        self.endDate = str((daystart + datetime.timedelta(days=1)).isoformat())
        self.stock_list_of_tweets_pair = {}

    def run(self):
        self.Market.awaitMarketOpen()
        self.Account.cancelAllOrders()
        self.strategy()

    def strategy(self):
        barsOfStocks = self.Market.getBarset(self.stock_list, self.barTimeframe, self.startDate, self.endDate)
        for stock in self.stock_list:
            timeList = []
            closeList = []
            volumeList = []
            bars = barsOfStocks[stock]
            for bar in bars:
                timeList.append(bar.t)
                closeList.append(bar.c)
                volumeList.append(bar.v)

            timeList =  pd.Series(timeList)
            closeList = pd.Series(closeList, dtype=np.float64)
            volumeList = pd.Series(volumeList, dtype=np.float64)
            EMA10 = ta.trend.EMAIndicator(closeList, 10).ema_indicator().values[-1]
            EMA20 = ta.trend.EMAIndicator(closeList, 20).ema_indicator().values[-1]

            print(EMA10)
            print(EMA20)