import tweepy
import json
import requests
import time
import os
import sys
import datetime
from dotenv import load_dotenv
import alpaca_trade_api as tradeapi
from Stocks import Stocks

load_dotenv()
API_KEY = os.getenv('API_KEY')
API_SECRET = os.getenv('API_SECRET')
APCA_API_BASE_URL = os.getenv('APCA_API_BASE_URL')

class MyStreamListener(tweepy.StreamListener):

    alpaca = tradeapi.REST(API_KEY, API_SECRET, APCA_API_BASE_URL, 'v2')
    stock_list = Stocks().get_stocks()
    stock_id_pair = {}
    stock_list_of_tweets_pair = {}
    stock_sentiment_score_pair = {}
    totalTweetsParsed = 1
    twitter_api = ""

    # get this from Azure text analytic resource
    sentiment_api_headers = {"Ocp-Apim-Subscription-Key": "49709452d4ae4864b5bd3a29278b4e6b"}
    sentiment_api_url = "https://autotrader-text-analytics.cognitiveservices.azure.com/text/analytics/v2.1/sentiment"

    for stock in stock_list:
        stock_id_pair.update({stock: 1})
        stock_list_of_tweets_pair.update({stock: []})
        stock_sentiment_score_pair.update({stock: 0})

    def on_error(self, status_code):
        print(status_code)

    def on_status(self, status):
        self.watch_for_market_close()

        if self.totalTweetsParsed % 200 == 0:
            self.process_sentiment_on_list()
            stocks_to_buy, stocks_to_sell = self.rebalance_stocks()
            self.batch_order(stocks_to_buy, stocks_to_sell)
            print('success!')


            for stock in self.stock_list:
                self.stock_list_of_tweets_pair.update({stock: []})

            time.sleep(60 * 30)

        for stock in self.stock_list:
            if stock in str(status.text):
                texts = {'language': 'en'}
                texts['id'] = self.stock_id_pair[stock]
                self.stock_id_pair[stock]+=1

                texts['text'] = status.text
                self.stock_list_of_tweets_pair[stock].append(texts)
                self.totalTweetsParsed += 1
                print(self.totalTweetsParsed)

    def process_sentiment_on_list(self):
        print("Analyzing tweets")

        for stock in self.stock_list:
            list_of_tweets = self.stock_list_of_tweets_pair[stock]
            if len(list_of_tweets) > 0:
                document = {'documents': list_of_tweets}
                scores = self.get_scores(document)
                total_score = 0

                if scores is not None:
                    for i in range(len(scores)):
                        score = scores[i]['score']
                        total_score+= score

                overall_sentiment_score =  total_score/ len(self.get_scores(document))
                self.stock_sentiment_score_pair[stock] = overall_sentiment_score

    def rebalance_stocks(self):
        stocks_to_buy = []
        stocks_to_sell = []
    
        for stock in self.stock_list:
            if self.stock_sentiment_score_pair[stock] > 0.66:
                # buy
                position = None
                try:
                    postion = self.alpaca.get_position(stock)
                except:
                    position = None

                if position:
                    if position.side == "long":
                        continue
                    else:
                        self.alpaca.close_position(stock)

                print("buying " + stock + ": " + str(self.stock_sentiment_score_pair[stock]))        
                stocks_to_buy.append(stock)
            else:
                # sell
                position = None
                try:
                    postion = self.alpaca.get_position(stock)
                except:
                    position = None

                if position:
                    if position.side == "long": 
                        self.alpaca.close_position(stock)
                    else:
                        continue
                print("selling " + stock + ": " + str(self.stock_sentiment_score_pair[stock]))
                stocks_to_sell.append(stock)
        return stocks_to_buy, stocks_to_sell

    def get_scores(self, document):
        response = requests.post(self.sentiment_api_url, headers=self.sentiment_api_headers, json=document)
        result = response.json()
        scores = json.loads(json.dumps(result))
        if 'documents' in scores:
            return scores['documents']

        return None

    def batch_order(self, stocks_to_buy, stocks_to_sell):
        stocks_to_buy_price = self.getTotalPrice(stocks_to_buy)
        stocks_to_sell_price = self.getTotalPrice(stocks_to_sell)

        equity = float(self.alpaca.get_account().equity)
        qty_to_buy = int(0.7 * equity // stocks_to_buy_price)
        qty_to_sell = int(0.3 * equity // stocks_to_sell_price)

        self.sendBatchOrder(qty_to_buy, stocks_to_buy, "buy")
        self.sendBatchOrder(qty_to_sell, stocks_to_sell, "sell")

    def sendBatchOrder(self, qty, stocks, side):
        for stock in stocks:
                self.submitOrder(qty,stock,side)

    def submitOrder(self, qty, stock, side):
        if(qty > 0):
            try:
                self.alpaca.submit_order(stock, qty, side, "market", "day")
                print("Market order of | " + str(qty) + " " +
                    stock + " " + side + " | completed.")
            except:
                print("Order of | " + str(qty) + " " + stock +
                    " " + side + " | did not go through. Retry....")
                self.alpaca.submit_order(stock, qty, side, "market", "day")
        else:
            print("Quantity is 0, order of | " + str(qty) +
                " " + stock + " " + side + " | not completed.")

    def getTotalPrice(self, stocks):
        totalPrice = 0
        for stock in stocks:
            bars = self.alpaca.get_barset(stock, "minute", 1)
            totalPrice += bars[stock][0].c
        return totalPrice

    def watch_for_market_close(self):
        # Figure out when the market will close so we can prepare to sell beforehand.
        clock = self.alpaca.get_clock()
        closingTime = clock.next_close.replace(
            tzinfo=datetime.timezone.utc).timestamp()
        currTime = clock.timestamp.replace(
            tzinfo=datetime.timezone.utc).timestamp()
        self.timeToClose = closingTime - currTime

        if(self.timeToClose < (60 * 15)):
            # Close all positions when 15 minutes til market close.
            print("Market closing soon.  Closing positions.")

            positions = self.alpaca.list_positions()
            for position in positions:
                if(position.side == 'long'):
                    orderSide = 'sell'
                else:
                    orderSide = 'buy'
                qty = abs(int(float(position.qty)))
                self.submitOrder(qty, position.symbol, orderSide)

            print("Sleeping until market close (15 minutes).")
            time.sleep(60 * 15)