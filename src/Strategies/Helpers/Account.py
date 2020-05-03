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

    def getPositions(self):
        return self.api.list_positions()

    def getPosition(self, symbol):
        return self.api.get_position(symbol)

    def cancelAllOrders(self):
        orders  = self.api.list_orders(status = "open")
        print("Closing all " + str(len(orders)) +  " open orders")
        for order in orders:
            self.api.cancel_order(order.id)

    def closePosition(self, stock):
        return self.api.close_position(stock)
        
    def closeAllPositions(self):
        return self.api.close_all_positions()

