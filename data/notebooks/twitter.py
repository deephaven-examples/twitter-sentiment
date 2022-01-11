from requests_oauthlib import OAuth1Session
import requests
from datetime import datetime

import time
import re
import json
from nltk.sentiment.vader import SentimentIntensityAnalyzer

from deephaven.DateTimeUtils import convertDateTime, minus, convertPeriod, currentTime
from deephaven import DynamicTableWriter
import deephaven.Types as dht
import threading

# Max results per time bin
max_results = 10

# Time intervals to split data
time_bins = 10

# How many days to go back. Max 7 for non-acemdic searches
time_history = 7


def create_headers(bearer_token):
        headers = {
            "Authorization": "Bearer {}".format(bearer_token),
            "User-Agent": "v2FullArchiveSearchPython"}
        return headers

search_url = "https://api.twitter.com/2/tweets/search/recent"

def connect_to_endpoint(url, headers, params):
    response = requests.request("GET", search_url, headers=headers, params=params)
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
    return response.json()

def get_tweets(query_params):
    headers = create_headers(bearer_token)
    json_response = connect_to_endpoint(search_url, headers, query_params)
    return(json_response['data'])


def analyze_line(text):
    sid = SentimentIntensityAnalyzer()
    tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
    return(sid.polarity_scores(text))

def get_query_params(start_time, end_time):
    return {'query': search_term,
                    'start_time': start_time,
                    'end_time': end_time,#'2021-12-18T00:00:00.000Z',
                    'max_results': max_results,
    #                'since_id': max_id,
    #                 'expansions': 'author_id,in_reply_to_user_id,geo.place_id',
                    'tweet.fields': 'id,text,author_id,in_reply_to_user_id,geo,conversation_id,created_at,lang,public_metrics,referenced_tweets,reply_settings,source',
                    'user.fields': 'id,name,username,created_at,description,public_metrics,verified',
    #                 'place.fields': 'full_name,id,country,country_code,geo,name,place_type',
                    'next_token': {}}


def cleanText(text):
    #to lowercase
    text = text.lower()
    #correct spaces (e.g. "End sentence.Begin another" becomes "End sentence. Begin another")
    text = re.sub(r'\.([a-zA-Z])', r'. \1', text)
    text = re.sub(r'\?([a-zA-Z])', r'. \1', text)
    text = re.sub(r'\!([a-zA-Z])', r'. \1', text)
    #replace q1,2,3,4 with q
    text = re.sub("q[1-4]", "q", text)
    #replace 20xx with 2000
    text = re.sub("20[0-2][0-9]", "2000", text)
    return text


def thread_func():
    for i in range(1, time_bins):
        start_time = str(minus(currentTime(),convertPeriod("T"+str(int(i*(24*time_history)/time_bins))+"H")))[:-9]+'Z'
        end_time = str(minus(currentTime(),convertPeriod("T"+str(int((i-1)*(24*time_history)/time_bins))+"H")))[:-9]+'Z'
        query_params = get_query_params(start_time, end_time)
        all_text = get_tweets(query_params)
        for t in all_text:
            id = float(t['id'])
            combined = analyze_line(cleanText(t['text']))
            negative = combined.get('neg')
            neutral = combined.get('neu')
            compound = combined.get('compound')
            positive = combined.get('pos')
            dateTime = t['created_at'][:-1]+" NY"
            retweet_count = t['public_metrics']['retweet_count']
            reply_count = t['public_metrics']['reply_count']
            like_count = t['public_metrics']['like_count']
            quote_count= t['public_metrics']['quote_count']
            tableWriter_sia.logRow(t['text'], float(compound), float(negative), float(neutral), float(positive), float(id),convertDateTime(dateTime), int(retweet_count), int(reply_count), int(like_count), int(quote_count))

thread_sia = threading.Thread(target = thread_func)
thread_sia.start()
