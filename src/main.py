from Strategies.SentAnalysisStrategy import SentAnalysisStrategy
from Strategies.MovingAverageStrategy import MovingAverageStrategy
from Strategies.RsiStrategy import RsiStrategy
from Strategies.GapStrategy import GapStrategy
from Strategies.IntradayStrategy import IntradayStrategy
from dotenv import load_dotenv
import alpaca_trade_api as tradeapi
import os

load_dotenv()
API_KEY = os.getenv('APCA_API_KEY_ID')
API_SECRET = os.getenv('APCA_API_SECRET_KEY')
APCA_API_BASE_URL = os.getenv('APCA_API_BASE_URL')


def main():
    api = tradeapi.REST(API_KEY, API_SECRET, APCA_API_BASE_URL, 'v2')
    print("Running Intraday strategy")
    strategy = IntradayStrategy(tradingApi=api)
    strategy.run()


if __name__ == '__main__':
    main()
