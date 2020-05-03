import collections
import enum

import pandas as pd
from src.Enums import OrderType


class MarketUtil:

    def GetHistoricalDailyData(self, account, lookBackInDays=7):
        return self.GetHistoricalData(account, 'day', lookBackInDays)

    def GetPercentChanges(self, account, timeframe='minute', limit=5):
        percent_changes = []
        stock_data = self.GetHistoricalData(account, timeframe, limit)
        for symbol in stock_data:
            percent = 100 * (stock_data[symbol].iloc[-1].close /
                       stock_data[symbol].iloc[0].close - 1)
            percent_changes.append((symbol, percent))
        percent_changes = sorted(
            percent_changes, key=lambda x: x[1], reverse=True)
        sorted_dict = collections.OrderedDict(percent_changes)
        return sorted_dict

    def GetCurrentData(self, account):
        return self.GetHistoricalData(account, 'minute', 1)

    def GetLivePrices(self, account):
        live_prices = {}
        stock_data = self.GetCurrentData(account)
        for symbol in stock_data:
            live_prices[symbol] = stock_data[symbol].loc[0].close
        return live_prices

    def GetHistoricalData(self, account, timeframe, limit, start=None, end=None, after=None, until=None):
        barset = account.api.get_barset(
            account.symbols, timeframe, limit, start, end, after, until)
        barset = self.FormatData(barset)
        return barset

    def FormatData(self, barset):
        dataframes = {}
        for symbol in barset.keys():
            bars = barset[symbol]
            data = {'close': [bar.c for bar in bars],
                    'high': [bar.h for bar in bars],
                    'low': [bar.l for bar in bars],
                    'open': [bar.o for bar in bars],
                    'time': [bar.t for bar in bars],
                    'volume': [bar.v for bar in bars]}
            dataframes[symbol] = pd.DataFrame(data)
        return dataframes

    def BuyStock(self, account, symbol, qty=1, type=OrderType.Market, price=0):
        if type is OrderType.Market:
            account.api.submit_order(symbol, qty, 'buy', 'market', 'day')
        elif type is OrderType.Limit:
            account.api.submit_order(symbol, qty, 'buy', 'limit', 'day', price)

    def SellStock(self, account, symbol, qty=1, type=OrderType.Market, price=0):
        if type is OrderType.Market:
            account.api.submit_order(symbol, qty, 'sell', 'market', 'day')
        elif type is OrderType.Limit:
            account.api.submit_order(
                symbol, qty, 'sell', 'limit', 'day', price)

    def SellAllStocks(self, account, symbols):
        positions = account.GetPositions()
        for position in positions:
            if position.symbol in symbols:
                self.SellStock(account, position.symbol, position.qty)
    
    def EmptyStocks(self, account):
        positions = account.GetPositions()
        for position in positions:
            self.SellStock(account, position.symbol, position.qty)

    def GetMarketClock(self, account):
        return account.api.get_clock()

    def IsMarketOpen(self, account):
        return self.GetMarketClock(account).is_open
