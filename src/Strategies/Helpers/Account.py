import math

class Account:
    def __init__(self, api):
        self.api = api

    def getAccount(self):
        return self.api.get_account()
    
    def getEquity(self):
        return float(self.getAccount().equity)

    def getCash(self):
        return float(self.getAccount().cash)

    def getBuyingPower(self):
        return float(self.getAccount().buying_power)

    def getLastEquity(self):
        return float(self.getAccount().last_equity)

    def getOrders(self):
        return self.api.list_orders()

    def getWatchlists(self):
        return self.api.get_watchlists()    
    
    def getWatchlistById(self, id='b5c1c3ef-a3ca-4e07-9e38-73fa71bd8c6e'):
        return self.api.get_watchlist(id)

    def getStocksFromWatchList(self):
        assets = self.getWatchlistById().assets
        stocks = []
        for asset in assets:
            stocks.append(asset['symbol'])
        return stocks
            
    def getPositions(self):
        return self.api.list_positions()

    def getPosition(self, symbol):
        return self.api.get_position(symbol)

    def cancelAllOrders(self):
        orders  = self.api.list_orders(status = "open")
        print("Cancelling all " + str(len(orders)) +  " open orders")
        for order in orders:
            self.api.cancel_order(order.id)

    def closePosition(self, stock):
        return self.api.close_position(stock)
        
    def closeAllPositions(self):
        return self.api.close_all_positions()

