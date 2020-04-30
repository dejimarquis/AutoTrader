import requests
import json
from dotenv import load_dotenv
import os

class SentimentAnalyzer:
    def __init__(self):
        load_dotenv()
        KEY = os.getenv('SENTIMENT_API_HEADER_KEY')
        self.sentiment_api_headers = {"Ocp-Apim-Subscription-Key": KEY}
        self.sentiment_api_url = "https://autotrader-text-analytics.cognitiveservices.azure.com/text/analytics/v2.1/sentiment"

    def getScores(self, document):
        response = requests.post(self.sentiment_api_url, headers=self.sentiment_api_headers, json=document)
        result = response.json()
        scores = json.loads(json.dumps(result))
        if 'documents' in scores:
            return scores['documents']

        return None