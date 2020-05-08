import pandas as pd
import ta
import datetime
import time
from pytz import timezone
import numpy as np
from .Helpers.Stocks import Stocks
from .Helpers.Market import Market
from .Helpers.Account import Account

class RsiStrategy:
    def __init__(self, tradingApi):
        eastern = timezone('US/Eastern')
        today = datetime.datetime.now()
        daystart = eastern.normalize(datetime.datetime(year=today.year, month=today.month,
                            day=today.day, hour=0, second=0, tzinfo=eastern))

        self.Account = Account(tradingApi)
        self.Market = Market(self.Account)
        self.stock_list = self.Market.getStocks()
        self.barTimeframe = "1Min"  # 1Min, 5Min, 15Min, 1H, 1D
        self.startDate = str(daystart.isoformat())
        self.endDate = str((daystart + datetime.timedelta(days=1)).isoformat())

    def run(self):
        self.Market.awaitMarketOpen()
        self.Account.cancelAllOrders()

        while(self.Market.isMarketOpen()):
            stocks_to_sell, stocks_to_buy = self.strategy()
            qtySell, qtyBuy = self.calculate_qty_to_buy_sell(stocks_to_sell, stocks_to_buy)
            self.Market.submitBatchOrder(qtySell, stocks_to_sell, "sell")
            self.Market.submitBatchOrder(qtyBuy, stocks_to_buy, "buy")
            time.sleep(20)

        print("Market is closed")
        print("Sleeping until market close (15 minutes).")
        time.sleep(60 * 15)

    def strategy(self):
        stocks_to_sell = []
        stocks_to_buy = []
        barsOfStocks = self.Market.getBarset(self.stock_list, self.barTimeframe, self.startDate, self.endDate)
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

            rsis = ta.momentum.RSIIndicator(closeList, 10).rsi().values if any(ta.momentum.RSIIndicator(closeList, 10).rsi().values) else None

            if any(rsis):
                v = [x for x in positions if x.symbol == stock]
                position = v[0] if any(v) else None

                if rsis[-2] < 30 and 30 < rsis[-1]: #oversold
                    if position:
                        if position.side == "long":
                            print("We already have a long position in "+ stock + ", so skip")
                            continue
                        else:
                            print("We have short position in " + stock + " already but we want to long, so closing current position")
                            self.Account.closePosition(stock)

                    print("Entering long position with  " + stock + " with RSI: " + str(rsis[-1]))        
                    stocks_to_buy.append(stock)
                elif rsis[-2] > 70 and 70 > rsis[-1]: #overbought
                    if position:
                        if position.side == "long": 
                            print("We have long position in " + stock + " already but we want to short, so closing current position")
                            self.Account.closePosition(stock)
                        else:
                            print("We already have a short position in "+ stock + ", so skip")
                            continue

                    print("Entering short position with  " + stock + "  with RSI: " + str(rsis[-1]))
                    stocks_to_sell.append(stock)
                elif position and position.side == "short" and rsis[-1] < 40: 
                    print("Exiting short position with RSI: " + str(rsis[-1]))
                    self.Account.closePosition(stock)                
                elif position and position.side == "long" and rsis[-1] > 60:
                    print("Exiting long positionw ith RSI: " + str(rsis[-1]))
                    self.Account.closePosition(stock)

        print("We are taking a short position in: " + str(stocks_to_sell))
        print("We are taking a long position in: " + str(stocks_to_buy))
        return stocks_to_sell, stocks_to_buy

    def calculate_qty_to_buy_sell(self, stocks_to_sell, stocks_to_buy):
        stocks_to_sell_price = self.Market.getTotalPrice(stocks_to_sell)
        stocks_to_buy_price = self.Market.getTotalPrice(stocks_to_buy)

        buyingPower = self.Account.getBuyingPower()
        qty_to_sell = int((0.5 * 0.2 * buyingPower) // (1.04 * stocks_to_sell_price)) if stocks_to_sell_price > 0 else 0 # 1.04 to account for fees
        qty_to_buy = int((0.5 * 0.2 * buyingPower) // (1.04 * stocks_to_buy_price)) if stocks_to_buy_price > 0 else 0

        return qty_to_sell, qty_to_buy