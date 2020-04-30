from Strategies.SentAnalysisStrategy import SentAnalysisStrategy
from dotenv import load_dotenv
import alpaca_trade_api as tradeapi
import os

load_dotenv()
API_KEY = os.getenv('API_KEY')
API_SECRET = os.getenv('API_SECRET')
APCA_API_BASE_URL = os.getenv('APCA_API_BASE_URL')

def main():
        api = tradeapi.REST(API_KEY, API_SECRET, APCA_API_BASE_URL, 'v2')
        strategy = SentAnalysisStrategy(tradingApi = api)
        strategy.run()

if __name__ == '__main__':
        main()