import alpaca_trade_api as tradeapi
import time
import datetime

class Market:
    def __init__(self, account):
        self.account = account
        self.api = account.api
        self.stockUniverse = ['DOMO', 'TLRY', 'SQ', 'MRO', 'AAPL', 'GM', 'SNAP', 'SHOP', 'SPLK', 'BA', 'AMZN', 'SUI', 'SUN', 'TSLA',
                         'CGC', 'SPWR', 'NIO', 'CAT', 'MSFT', 'PANW', 'OKTA', 'TWTR', 'TM', 'TDOC', 'ATVI', 'GS', 'BAC', 'MS', 'TWLO', 'QCOM', ]
    
    def getStocks(self):
        return self.stockUniverse

    def getStocksGivenBudget(self, budget):
        return self.selectStocks(budget, len(self.stockUniverse) - 1, [])

    def selectStocks(self, budget, index, selectedStocks):
        if budget <= 0 or index < 0 or not self.stockUniverse:
            return selectedStocks
        if self.getCurrentPrice(self.stockUniverse[index]) > budget:
            return self.selectStocks(budget, index, selectedStocks)

        s0 = self.selectStocks(budget
                                    , index - 1
                                    , selectedStocks)
        s1 = self.selectStocks(budget - self.getCurrentPrice(self.stockUniverse[index])
                                    , index - 1
                                    , selectedStocks.append(self.stockUniverse[index]))
        x =  max(self.getTotalPrice(s0), self.getTotalPrice(s1))

        if x == self.getTotalPrice(s0):
            return s0
        else:
            return s1

    def getCurrentPrice(self, stock):
        bars = self.api.get_barset(stock, "minute", 1)
        return bars[stock][0].c

    def getTotalPrice(self, stocks):
        totalPrice = 0
        for stock in stocks:
            totalPrice += self.getCurrentPrice(stock)
        return totalPrice

    def getBarset(self, stocks, barTimeframe, start=None, end=None):
        bars = self.api.get_barset(stocks, barTimeframe,start=start, end=end)
        return bars

    def getMarketClock(self):
        return self.api.get_clock()

    def isMarketOpen(self):
        return self.getMarketClock().is_open

    def submitBatchOrder(self, qty, stocks, side):
        for stock in stocks:
                self.submitOrder(qty,stock,side)

    def submitOrder(self, qty, stock, side):
        if(qty > 0):
            try:
                self.api.submit_order(stock, qty, side, "market", "day")
                print("Market order of | " + str(qty) + " " +
                    stock + " " + side + " | completed.")
            except:
                print("Order of | " + str(qty) + " " + stock +
                    " " + side + " | did not go through. Retrying....")
                try:
                    self.api.submit_order(stock, qty, side, "market", "day")
                except Exception as e:
                    print("Order of | " + str(qty) + " " + stock +
                    " " + side + " | STILL did not go through. ...." + str(e))
        else:
            print("Quantity is 0, order of | " + str(qty) +
                " " + stock + " " + side + " | not completed.")

    def awaitMarketOpen(self):
        isOpen = self.isMarketOpen()
        while(not isOpen):
            clock = self.getMarketClock()
            openingTime = clock.next_open.replace(
                tzinfo=datetime.timezone.utc).timestamp()
            currTime = clock.timestamp.replace(
                tzinfo=datetime.timezone.utc).timestamp()
            timeToOpen = int((openingTime - currTime) / 60)

            print(str(timeToOpen) + " minutes till market open.")
            time.sleep(60)
            isOpen = self.getMarketClock().is_open

    def timeToClose(self):
        clock = self.getMarketClock()
        closingTime = clock.next_close.replace(
            tzinfo=datetime.timezone.utc).timestamp()
        currTime = clock.timestamp.replace(
            tzinfo=datetime.timezone.utc).timestamp()
        timeToClose = closingTime - currTime

        return timeToClose

    def aboutToClose(self):
        return self.timeToClose() < (60 * 15)