import time
import datetime
import pytz
import pandas as pd
from .Helpers.Stocks import Stocks
from .Helpers.Market import Market
from .Helpers.Account import Account

class IntradayStrategy:
    def __init__(self, tradingApi):
        TZ = 'America/New_York'
        today = datetime.datetime.now(tz=pytz.timezone(TZ))
        beg = datetime.datetime(year=today.year, month=today.month,
                            day=today.day, hour=9, minute=30, second=0)
        close = datetime.datetime(year=today.year, month=today.month,
                            day=today.day, hour=9, minute=44, second=59)
        
        self.Account = Account(tradingApi)
        self.Market = Market(self.Account)
        self.stock_list = self.Market.getStocks()
        self.barTimeframe = "15Min"  # 1Min, 5Min, 15Min, 1H, 1D
        self.start = pd.Timestamp(beg, tz=TZ).isoformat()
        self.end = pd.Timestamp(close, tz=TZ).isoformat()

    def run(self):
        self.Market.awaitMarketOpen()
        self.Account.cancelAllOrders()
        self.strategy()

    def strategy(self):
        time.sleep((15*60) + 5)

        barsOfStocks = self.Market.getBarset(self.stock_list, self.barTimeframe, 1, self.start, self.end)
        qty_to_buy = self.Market.calculate_qty_to_buy(self.Account.getEquity(), self.stock_list)

        while not self.Market.aboutToClose():
            for stock in self.stock_list:
                try:
                    position = self.Account.getPosition(stock)
                    print("We have a " + str(position.side) + " position in " + stock+ " so skip")
                    continue
                except Exception:
                    pass

                stockCurrentPrice = self.Market.getCurrentPrice(stock)
                if stockCurrentPrice > barsOfStocks[stock][0].h:
                    stop_loss = {"stop_price": barsOfStocks[stock][0].h}
                    take_profit = {"limit_price": stockCurrentPrice * 1.01}
                    self.Market.submitOrder(qty_to_buy[stock], stock, "buy", order_class="bracket", stop_loss=stop_loss, take_profit=take_profit)

                elif stockCurrentPrice < barsOfStocks[stock][0].l:
                    stop_loss = {"stop_price": barsOfStocks[stock][0].l}
                    take_profit = {"limit_price": stockCurrentPrice * .99}
                    self.Market.submitOrder(qty_to_buy[stock], stock, "sell", order_class="bracket", stop_loss=stop_loss, take_profit=take_profit)

            time.sleep(10)

        print("Market closing soon.  Closing positions.")
        self.Account.closeAllPositions()
        print("Sleeping until market close (15 minutes).")
        time.sleep(60 * 15)