from Strategies.SentAnalysisStrategy import SentAnalysisStrategy
from Strategies.MovingAverageStrategy import MovingAverageStrategy
from dotenv import load_dotenv
import alpaca_trade_api as tradeapi
import os

load_dotenv()
API_KEY = os.getenv('API_KEY')
API_SECRET = os.getenv('API_SECRET')
APCA_API_BASE_URL = os.getenv('APCA_API_BASE_URL')


def main():
    api = tradeapi.REST(API_KEY, API_SECRET, APCA_API_BASE_URL, 'v2')
    try:
        print("Running moving average strategy")
        strategy = MovingAverageStrategy(tradingApi=api)
        strategy.run()
    except Exception as ex:
        print(str(ex) +  "Moving average strategy failed, switch to sentimental ....")
        strategy = SentAnalysisStrategy(tradingApi=api)
        strategy.run()


if __name__ == '__main__':
    main()
