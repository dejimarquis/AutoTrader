import math
from src.Enums import MarketStrategy

class Account:
    def __init__(self, api):
        self.api = api
        #self.symbols = ['AAPL', 'TSLA', 'MSFT']
        self.symbols = ['DOMO', 'TLRY', 'SQ', 'MRO', 'AAPL', 'GM', 'SNAP', 'SHOP', 'SPLK', 'BA', 'AMZN', 'SUI', 'SUN', 'TSLA',
                         'CGC', 'SPWR', 'NIO', 'CAT', 'MSFT', 'PANW', 'OKTA', 'TWTR', 'TM', 'TDOC', 'ATVI', 'GS', 'BAC', 'MS', 'TWLO', 'QCOM']
        self.buget_percentages = { MarketStrategy.Momentum: 0.5 }

    def GetAccount(self):
        return self.api.get_account()
    
    def GetEquity(self):
        return float(self.GetAccount().equity)

    def GetCash(self):
        return float(self.GetAccount().cash)

    def GetBuyingPower(self):
        return float(self.GetAccount().buying_power)

    def GetBudget(self, strategy):
        buying_power = self.GetBuyingPower()
        return math.floor(self.buget_percentages[strategy] * buying_power)

    def GetLastEquity(self):
        return float(self.GetAccount().last_equity)

    def GetOrders(self):
        return self.api.list_orders()

    def GetPositions(self):
        return self.api.list_positions()

    def CloseAllOrders(self):
        orders  = self.api.list_orders(status = "open")
        print("Closing all " + str(len(orders)) +  " open orders")
        for order in orders:
            self.api.cancel_order(order.id)
