import os
import sys
import tweepy
import datetime
import time
import MyStreamListener
from Stocks import Stocks
from dotenv import load_dotenv
import alpaca_trade_api as tradeapi
from Stocks import Stocks

API_KEY = os.getenv('API_KEY')
API_SECRET = os.getenv('API_SECRET')
APCA_API_BASE_URL = os.getenv('APCA_API_BASE_URL')

class SentAnalysisOnStocks:
    def __init__(self, request_limit=20):
        load_dotenv()
        API_KEY = os.getenv('API_KEY')
        API_SECRET = os.getenv('API_SECRET')
        APCA_API_BASE_URL = os.getenv('APCA_API_BASE_URL')

        self.request_limit = request_limit
        self.api = ""
        self.twitter_keys = {
            'consumer_key': os.getenv('TWITTER_API_KEY'),
            'consumer_secret': os.getenv('TWITTER_API_SECRET'),
            'access_token_key': os.getenv('TWITTER_ACCESS_TOKEN_KEY'),
            'access_token_secret': os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
        }
        self.set_up_creds()
        self.alpaca = tradeapi.REST(API_KEY, API_SECRET, APCA_API_BASE_URL, 'v2')

    def set_up_creds(self):
        auth = tweepy.OAuthHandler(self.twitter_keys['consumer_key'], self.twitter_keys['consumer_secret'])
        auth.set_access_token(self.twitter_keys['access_token_key'], self.twitter_keys['access_token_secret'])
        self.api = tweepy.API(auth)

    def run(self):
        self.awaitMarketOpen()
        self.alpaca.close_all_positions()
        self.get_tweets_and_perform_sent_analysis()

    def awaitMarketOpen(self):
        isOpen = self.alpaca.get_clock().is_open
        while(not isOpen):
            clock = self.alpaca.get_clock()
            openingTime = clock.next_open.replace(
                tzinfo=datetime.timezone.utc).timestamp()
            currTime = clock.timestamp.replace(
                tzinfo=datetime.timezone.utc).timestamp()
            timeToOpen = int((openingTime - currTime) / 60)
            print(str(timeToOpen) + " minutes till market open.")
            time.sleep(60)
            isOpen = self.alpaca.get_clock().is_open

    def get_tweets_and_perform_sent_analysis(self):
        myStreamListener = MyStreamListener.MyStreamListener()
        myStreamListener.twitter_api = self.api
        myStream = tweepy.Stream(auth=self.api.auth, listener=myStreamListener)
        symbolList = ["$"+s for s in Stocks().get_stocks()]
        myStream.filter(track= symbolList,
                        languages=['en'], is_async=True)


if __name__ == '__main__':
        strategy = SentAnalysisOnStocks()
        strategy.run()