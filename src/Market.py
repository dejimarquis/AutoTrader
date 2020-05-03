import threading
import time
import datetime
import math
from src.Account import Account
from src.Enums import MarketStrategy
from src.MarketUtil import MarketUtil
from src.MarketTracker import  MarketTracker


class Market:

    def __init__(self):
        self.util = MarketUtil()
        self.marketTracker = MarketTracker()

    def Run(self, account, strategy=MarketStrategy.Momentum):
        lookBackWindowInMins = 2
        marketCloseWindowInMins = 10
        while True:
            account.CloseAllOrders()
            self.WaitForOpen(account)
            print("Market is open!")
            while self.util.IsMarketOpen(account):
                self.MomentumMarket(account, 'minute', lookBackWindowInMins)
                time.sleep(60 * lookBackWindowInMins)
                if self.IsMarketAboutToClose(account, marketCloseWindowInMins):
                    print("Market is about to close...selling all stocks")
                    self.util.EmptyStocks(account)
                    print("Sleeping until market close.")
                    time.sleep(60 * marketCloseWindowInMins)
            print("Market has closed!")
            self.marketTracker.Reset()

    def MomentumMarket(self, account, timeframe='minute', lookBackWindow=5):
        percent_changes = self.util.GetPercentChanges(account, timeframe, lookBackWindow)
        stocksToSell, stocksToBuy, stocksToKeep = self.marketTracker.Update(percent_changes)
        self.Sell(account, stocksToSell)
        self.Buy(account, stocksToBuy)
        self.Keep(account, stocksToKeep)
    
    def Keep(self, account, stocksToKeep):
        print("Keeping stocks: " + ', '.join(stocksToKeep.keys()))

    def Sell(self, account, stocksToSell):
        stocksToSell = {k: v for k, v in stocksToSell.items() if v <0} #sell the ones which are recommended and have a negative change
        symbolsToSell = stocksToSell.keys()
        print("Selling stocks: " + ', '.join(symbolsToSell))
        self.util.SellAllStocks(account, symbolsToSell)

    def Buy(self, account, stocksToBuy):
        stocksToBuy = {k: v for k, v in stocksToBuy.items() if v >0} #Todo find a way to include stocks that have a most recent negative change
        print("Buying stocks: " + ', '.join(stocksToBuy.keys()))
        total_increase_sum = sum(stocksToBuy.values())
        shares_to_buy = {}
        budget = account.GetBudget(MarketStrategy.Momentum)
        live_prices = self.util.GetLivePrices(account)
        for symbol in stocksToBuy:
            # split the budget for each of the stocks: Shares[s] = B * (P(s)/ Sum(P) * C(b))
            shares_to_buy[symbol] = budget * \
                (stocksToBuy[symbol] /
                 (total_increase_sum * live_prices[symbol]))
            # Get the floor since we can't buy fractional shares
            shares_to_buy[symbol] = math.floor(shares_to_buy[symbol])
        for symbol in shares_to_buy:
            if(shares_to_buy[symbol]> 0):
                self.util.BuyStock(account, symbol, shares_to_buy[symbol])

    def WaitForOpen(self, account):
        isOpen = self.util.IsMarketOpen(account)
        while(not isOpen):
            clock = self.util.GetMarketClock(account)
            openingTime = clock.next_open.replace(
                tzinfo=datetime.timezone.utc).timestamp()
            currTime = clock.timestamp.replace(
                tzinfo=datetime.timezone.utc).timestamp()
            timeToOpen = int((openingTime - currTime) / 60)
            print(str(timeToOpen) + " minutes until market opens.")
            time.sleep(60)
            isOpen = self.util.IsMarketOpen(account)
    
    def IsMarketAboutToClose(self, account, marketCloseWindowInMins):
        clock = self.util.GetMarketClock(account)
        closingTime = clock.next_close.replace(
                tzinfo=datetime.timezone.utc).timestamp()
        currTime = clock.timestamp.replace(
            tzinfo=datetime.timezone.utc).timestamp()
        timeToClose = closingTime - currTime
        return timeToClose < (60 * marketCloseWindowInMins)

