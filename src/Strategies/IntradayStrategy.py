import time
from .Helpers.Stocks import Stocks
from .Helpers.Market import Market
from .Helpers.Account import Account

class IntradayStrategy:
    def __init__(self, tradingApi):
        self.Account = Account(tradingApi)
        self.Market = Market(self.Account)
        self.stock_list = self.Market.getStocks()
        self.barTimeframe = "15Min"  # 1Min, 5Min, 15Min, 1H, 1D

    def run(self):
        self.Market.awaitMarketOpen()
        self.Account.cancelAllOrders()
        self.strategy()

    def strategy(self):
        time.sleep(16*60)
        barsOfStocks = self.Market.getBarset(self.stock_list, self.barTimeframe, 1)
        time.sleep(60)

        while not self.Market.aboutToClose():
            for stock in self.stock_list:
                stockCurrentPrice = self.Market.getCurrentPrice(stock)
                if stockCurrentPrice > barsOfStocks[stock][0].h:
                    qty_to_buy = self.Market.calculate_qty_to_buy(self.Account.buyingPower, [stock])
                    stop_loss = {'stop_price': (barsOfStocks[stock][0].h + barsOfStocks[stock][0].l)/2}
                    take_profit = {'limit_price': stockCurrentPrice * 1.01}
                    self.Market.submitOrder(qty_to_buy[stock], stock, "buy", stop_loss=stop_loss, take_profit=take_profit)
                    self.stock_list.remove(stock)
                elif stockCurrentPrice < barsOfStocks[stock][0].l:
                    qty_to_buy = self.Market.calculate_qty_to_buy(self.Account.buyingPower, [stock])
                    stop_loss = {'stop_price': (barsOfStocks[stock][0].h + barsOfStocks[stock][0].l)/2}
                    take_profit = {'limit_price': stockCurrentPrice * .99}
                    self.Market.submitOrder(qty_to_buy[stock], stock, "sell", stop_loss=stop_loss, take_profit=take_profit)
                    self.stock_list.remove(stock)
            time.sleep(30)

        print("Market closing soon.  Closing positions.")
        self.Account.closeAllPositions()
        print("Sleeping until market close (15 minutes).")
        time.sleep(60 * 15)