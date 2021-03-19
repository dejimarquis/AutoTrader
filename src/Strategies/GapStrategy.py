import pandas as pd
import ta
import datetime
import time
from pytz import timezone
import numpy as np
from .Helpers.Stocks import Stocks
from .Helpers.Market import Market
from .Helpers.Account import Account

class GapStrategy:
    def __init__(self, tradingApi):
        self.Account = Account(tradingApi)
        self.Market = Market(self.Account)
        self.stock_list = self.Account.getStocksFromWatchList()
        self.barTimeframe = "1Min"  # 1Min, 5Min, 15Min, 1H, 1D

    def run(self):
        self.Market.awaitMarketOpen()
        self.Account.cancelAllOrders()

        # Buys all the top pre-market gaining stocks when the market opens
        qtySell, qtyBuy = self.Market.calculate_qty_to_buy_sell([], self.stock_list)
        self.Market.submitBatchOrder(qtyBuy, self.stock_list, "buy")
        time.sleep(20)

        while(not self.Market.aboutToClose()):
            stocks_to_sell, stocks_to_buy = self.strategy()
            qtySell, qtyBuy = self.Market.calculate_qty_to_buy_sell(stocks_to_sell, stocks_to_buy)
            self.Market.submitBatchOrder(qtySell, stocks_to_sell, "sell")
            self.Market.submitBatchOrder(qtyBuy, stocks_to_buy, "buy")
            time.sleep(20)

        print("Market closing soon.  Closing positions.")
        self.Account.closeAllPositions()
        print("Sleeping until market close (15 minutes).")
        time.sleep(60 * 15)

    def strategy(self):
        stocks_to_sell = []
        stocks_to_buy = []
        barsOfStocks = self.Market.getBarset(self.stock_list, self.barTimeframe)
        positions = self.Account.getPositions()
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
            EMA10 = ta.trend.EMAIndicator(closeList, 10).ema_indicator().values[-1] if any(ta.trend.EMAIndicator(closeList, 10).ema_indicator().values) else 0
            EMA20 = ta.trend.EMAIndicator(closeList, 20).ema_indicator().values[-1] if any(ta.trend.EMAIndicator(closeList, 20).ema_indicator().values) else 0

            position = None
            try:
                v = [x for x in positions if x.symbol == stock]
                position = v[0] if any(v) else None
            except Exception as e:
                print(str(stock) + " " + str(e))
                position = None

            if EMA10 > EMA20:
                # buy
                if position:
                    if position.side == "long":
                        print("We already have a long position in "+ stock + ", so skip")
                        continue
                    else:
                        print("We have short position in " + stock + " already but we want to long, so closing current position")
                        self.Account.closePosition(stock)

                print("buying " + stock + " with EMA10: " + str(EMA10) + " and EMA20: " + str(EMA20))        
                stocks_to_buy.append(stock)
            else:
                # sell
                if position:
                    if position.side == "long": 
                        print("We have long position in " + stock + " already but we want to short, so closing current position")
                        self.Account.closePosition(stock)
                    else:
                        print("We already have a short position in "+ stock + ", so skip")
                        continue

                print("selling " + stock + "  with EMA10: " + str(EMA10) + " and EMA20: " + str(EMA20))
                stocks_to_sell.append(stock)

        print("We are taking a short position in: " + str(stocks_to_sell))
        print("We are taking a long position in: " + str(stocks_to_buy))
        return stocks_to_sell, stocks_to_buy