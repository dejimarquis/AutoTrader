import os
import alpaca_trade_api as tradeapi
from src.Account import Account
from src.Market import Market
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('API_KEY')
API_SECRET = os.getenv('API_SECRET')
APCA_API_BASE_URL = os.getenv('APCA_API_BASE_URL')
VERSION = 'v2'

API_KEY = os.getenv('API_KEY')
API_SECRET = os.getenv('API_SECRET')
APCA_API_BASE_URL = os.getenv('APCA_API_BASE_URL')
def main():
    api = tradeapi.REST(API_KEY, API_SECRET, APCA_API_BASE_URL, VERSION)
    myAccount = Account(api)
    market = Market()
    market.Run(myAccount)    

if __name__ == "__main__": 
    main()