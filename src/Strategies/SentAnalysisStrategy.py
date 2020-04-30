import tweepy
import datetime
import time
import os
from .MyStreamListener import MyStreamListener
from .Helpers.Stocks import Stocks
from .Helpers.Market import Market
from .Helpers.Account import Account

class SentAnalysisStrategy:
    def __init__(self, tradingApi, request_limit=20):

        self.request_limit = request_limit
        self.api = ""
        self.twitter_keys = {
            'consumer_key': os.getenv('TWITTER_API_KEY'),
            'consumer_secret': os.getenv('TWITTER_API_SECRET'),
            'access_token_key': os.getenv('TWITTER_ACCESS_TOKEN_KEY'),
            'access_token_secret': os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
        }
        self.set_up_creds()
        self.Account = Account(tradingApi)
        self.Market = Market(self.Account)

    def set_up_creds(self):
        auth = tweepy.OAuthHandler(self.twitter_keys['consumer_key'], self.twitter_keys['consumer_secret'])
        auth.set_access_token(self.twitter_keys['access_token_key'], self.twitter_keys['access_token_secret'])
        self.api = tweepy.API(auth)

    def run(self):
        self.Market.awaitMarketOpen()
        self.Account.closeAllOrders()
        self.get_tweets_and_perform_sent_analysis()

    def get_tweets_and_perform_sent_analysis(self):
        myStreamListener = MyStreamListener(self.Account, self.Market)
        myStream = tweepy.Stream(auth=self.api.auth, listener=myStreamListener)
        symbolList = ["$"+s for s in Stocks().getStocks()]
        myStream.filter(track= symbolList,
                        languages=['en'], is_async=True)
