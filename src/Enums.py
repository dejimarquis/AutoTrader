import enum 

class MarketStrategy(enum.Enum):
    Momentum = 1

class OrderType(enum.Enum):
    Market = 1
    Limit = 2
