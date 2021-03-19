import alpaca_trade_api as tradeapi
import time
import datetime

class Market:
    def __init__(self, account):
        self.account = account
        self.api = account.api
        self.stockUniverse = ['NFLX', 'NVDA', 'SQ', 'MRO', 'AAPL', 'GM', 'SNAP', 'SHOP', 'SPLK', 'BA', 'AMZN', 'TSLA',
                                'ROKU', 'RIOT', 'NIO', 'CAT', 'MSFT', 'MRNA', 'AMC', 'TWTR', 'MS', 'TWLO', 'QCOM', 'GME']
        self.stock_price_pair = {}
        self.setStockPricePair()
    
    def getStocks(self):
        return self.stockUniverse

    def getStocksGivenBudget(self, budget):
        return self._selectStocks(budget, len(self.stockUniverse) - 1, [])

    def setStockPricePair(self):
        for stock in self.stockUniverse:
            self.stock_price_pair.update({stock: self.getCurrentPrice(stock)})

    def getCurrentPrice(self, stock):
        bars = self.api.get_barset(stock, "minute", 1)
        return bars[stock][0].c

    def getTotalPrice(self, stocks):
        totalPrice = 0
        for stock in stocks:
            totalPrice += self.getCurrentPrice(stock)
        return totalPrice

    def getBarset(self, stocks, barTimeframe, limit=480):
        bars = self.api.get_barset(stocks, barTimeframe, limit=limit)
        return bars

    def getMarketClock(self):
        return self.api.get_clock()

    def calculate_qty_to_buy_sell(self, stocks_to_sell, stocks_to_buy):
        stocks_to_sell_price = self.getTotalPrice(stocks_to_sell)
        stocks_to_buy_price = self.getTotalPrice(stocks_to_buy)

        buyingPower = self.account.getEquity()
        qty_to_sell = int((0.05 * len(stocks_to_sell) * buyingPower) // (1.04 * stocks_to_sell_price)) if stocks_to_sell_price > 0 and buyingPower > 0 else 0 # 1.04 to account for fees
        qty_to_buy = int((0.05 * len(stocks_to_buy) * buyingPower) // (1.04 * stocks_to_buy_price)) if stocks_to_buy_price > 0 and buyingPower > 0 else 0

        return qty_to_sell, qty_to_buy

    def calculate_qty_to_buy(self, buyingPower, stocks_to_buy):
        amt_to_spend_per_stock = buyingPower/len(stocks_to_buy)
        stock_qty_pair = {}

        for stock in stocks_to_buy:
            stock_qty_pair.update({stock: int(amt_to_spend_per_stock // (self.getCurrentPrice(stock) * 1.04))})

        return stock_qty_pair

    def isMarketOpen(self):
        return self.getMarketClock().is_open

    def submitBatchOrder(self, qty, stocks, side):
        for stock in stocks:
                self.submitOrder(qty,stock,side)

    def submitOrder(self, qty, stock, side, stop_loss=None, take_profit=None):
        if(qty > 0):
            try:
                if side == 'buy':
                    self.api.submit_order(stock, qty, side, "market", "day", stop_loss=stop_loss, take_profit=take_profit)
                elif side == 'sell':
                    self.api.submit_order(stock, qty, side, "market", "day", stop_loss=stop_loss, take_profit=take_profit)
                print("Market order of | " + str(qty) + " " +
                    stock + " " + side + " | completed.")
            except:
                print("Order of | " + str(qty) + " " + stock +
                    " " + side + " | did not go through. Retrying....")
                try:
                    if side == 'buy':
                        self.api.submit_order(stock, qty, side, "market", "day", stop_loss=stop_loss, take_profit=take_profit)
                    elif side == 'sell':
                        self.api.submit_order(stock, qty, side, "market", "day", stop_loss=stop_loss, take_profit=take_profit)
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

    def _selectStocks(self, budget, index, selectedStocks):
        if budget <= 0 or index < 0 or not self.stockUniverse:
            return selectedStocks
        if self.stock_price_pair[self.stockUniverse[index]] > budget:
            return self._selectStocks(budget, index, selectedStocks)

        s0 = self._selectStocks(budget
                                    , index - 1
                                    , selectedStocks)
        s1 = self._selectStocks(budget - self.stock_price_pair[self.stockUniverse[index]]
                                    , index - 1
                                    , selectedStocks.append(self.stockUniverse[index]))
        x =  max(self.getTotalPrice(s0), self.getTotalPrice(s1))

        if x == self.getTotalPrice(s0):
            return s0
        else:
            return s1