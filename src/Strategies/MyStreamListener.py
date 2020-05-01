import tweepy
import json
import time
import datetime
from .Helpers.Stocks import Stocks
from .Helpers.Market import Market
from .Helpers.Account import Account
from .Helpers.SentimentAnalyzer import SentimentAnalyzer

class MyStreamListener(tweepy.StreamListener):
    def __init__(self, account, market, api=None):
        super().__init__(api=api)
        self.Account = account
        self.Market = market
        self. Sent = SentimentAnalyzer()
        self.stock_list = Stocks().getStocks()
        self.stock_id_pair = {}
        self.stock_list_of_tweets_pair = {}
        self.stock_sentiment_score_pair = {}
        self.totalTweetsParsed = 0
        for stock in self.stock_list:
            self.stock_id_pair.update({stock: 1})
            self.stock_list_of_tweets_pair.update({stock: []})
            self.stock_sentiment_score_pair.update({stock: 0})

    def on_error(self, status_code):
        print(status_code)

    def on_status(self, status):
        if self.Market.aboutToClose():
            print("Market closing soon.  Closing positions.")
            self.Account.closeAllPositions()
            print("Sleeping until market close (15 minutes).")
            time.sleep(60 * 15)

        if self.totalTweetsParsed > 0 and self.totalTweetsParsed % 200 == 0:
            self.process_sentiment_on_list(self.stock_list_of_tweets_pair)
            stocks_to_sell, stocks_to_buy = self.rebalance_stocks()
            qtySell, qtyBuy = self.calculate_qty_to_buy_sell(stocks_to_sell, stocks_to_buy)
            self.Market.submitBatchOrder(qtySell, stocks_to_sell, "sell")
            self.Market.submitBatchOrder(qtyBuy, stocks_to_buy, "buy")
            
            print('success!')
            for stock in self.stock_list:
                self.stock_list_of_tweets_pair.update({stock: []})
            if self.Market.timeToClose() < 60 * 30:
                time.sleep(60 * 10)
            else:
                time.sleep(60 * 15)

        for stock in self.stock_list:
            if stock in str(status.text):
                texts = {'language': 'en'}
                texts['id'] = self.stock_id_pair[stock]
                texts['text'] = status.text
                self.stock_list_of_tweets_pair[stock].append(texts)
                self.stock_id_pair[stock]+=1
                self.totalTweetsParsed += 1
                print(self.totalTweetsParsed)

    def process_sentiment_on_list(self, stock_list_of_tweets_pair):
        print("Analyzing tweets")

        for stock in self.stock_list:
            list_of_tweets = stock_list_of_tweets_pair[stock]
            if len(list_of_tweets) > 0:
                document = {'documents': list_of_tweets}
                scores = self.Sent.getScores(document)
                total_score = 0

                if scores is not None:
                    for i in range(len(scores)):
                        score = scores[i]['score']
                        total_score+= score

                overall_sentiment_score =  total_score/ len(self.Sent.getScores(document))
                self.stock_sentiment_score_pair.update({stock: overall_sentiment_score})

    def rebalance_stocks(self):
        stocks_to_sell = []
        stocks_to_buy = []
    
        for stock in self.stock_list:
            sentimentScore = self.stock_sentiment_score_pair[stock]
            if sentimentScore > 0:
                if sentimentScore > 0.5:
                    # buy
                    position = None
                    try:
                        postion = self.Account.getPosition(stock)
                    except Exception as e:
                        print(stock + " " + str(e))
                        position = None

                    if position:
                        if position.side == "long":
                            continue
                        else:
                            print("We have short position in " + stock + " already but we want to long, so closing current position")
                            self.Account.closePosition(stock)

                    print("buying " + stock + " with sentimental score: " + str(self.stock_sentiment_score_pair[stock]))        
                    stocks_to_buy.append(stock)
                else:
                    # sell
                    position = None
                    try:
                        postion = self.Account.getPosition(stock)
                    except Exception as e:
                        print(stock + " " + str(e))
                        position = None

                    if position:
                        if position.side == "long": 
                            print("We have long position in " + stock + " already but we want to short, so closing current position")
                            self.Account.closePosition(stock)
                        else:
                            continue

                    print("selling " + stock + " with sentimental score: "  + str(self.stock_sentiment_score_pair[stock]))
                    stocks_to_sell.append(stock)

        print("We are taking a short position in: " + str(stocks_to_sell))
        print("We are taking a long position in: " + str(stocks_to_buy))
        return stocks_to_sell, stocks_to_buy

    def calculate_qty_to_buy_sell(self, stocks_to_sell, stocks_to_buy):
        stocks_to_sell_price = self.Market.getTotalPrice(stocks_to_sell)
        stocks_to_buy_price = self.Market.getTotalPrice(stocks_to_buy)

        buyingPower = self.Account.getEquity()
        qty_to_sell = int(0.3 * buyingPower // stocks_to_sell_price) if stocks_to_sell_price > 0 else 0
        qty_to_buy = int(1.3 * buyingPower // stocks_to_buy_price) if stocks_to_buy_price > 0 else 0

        return qty_to_sell, qty_to_buy
