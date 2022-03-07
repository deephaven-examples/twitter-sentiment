# twitter-sentiment

This repository integrates [Deephaven](http://deephaven.io/) with [Twitter](https://twitter.com/) and [Python's Natural Language Toolkit (NLTK)](https://www.nltk.org/) to pull recent tweets and evaluate sentiment in real-time. We start by pulling the data and running a `SentimentIntensityAnalyzer` on each tweet. We then aggregate the posts to see the overall positivity or negativity of that term on Twitter with time.
 Running `./twitter-sentiment.sh` will create open deephaven on [http://localhost:10000/ide](http://localhost:10000/ide).

## How it works


### Components

* `Dockerfile` - The Dockerfile for the application. This extends the default Deephaven images to add dependencies. See our guide, [How to install Python packages](https://deephaven.io/core/docs/how-to-guides/install-python-packages/#add-packages-to-a-custom-docker-image), for more information.
* `docker-compose.yml` - The Docker Compose file for the application. This is mostly the same as the [Deephaven docker-compose file](https://raw.githubusercontent.com/deephaven/deephaven-core/main/containers/python-examples/docker-compose.yml) with modifications to run (NLTK)](https://www.nltk.org/) with [Twitter V2 API](https://twitter.com/) and custom dependencies.
* `twitter-sentiment.sh` - A simple helper script to launch the application.
* `data/notebooks/keys.py` - A query to install (NLTK)](https://www.nltk.org/) and set tokens keys and search term.  This script needs to be edited for user information.
* `data/notebooks/finnhub.py` - A Deephaven sample query to pull crypto data from [Finnhub](https://finnhub.io/) based on search term.
* `data/notebooks/graphing.py` - A Deephaven sample query to aggregate and graph twitter sentiment information.
* `data/notebooks/learn-twitter.py` - A Deephaven sample query to run AI on the data.
* `data/notebooks/twitter.py` - A Deephaven sample query to pull Tweets.
* `requirements.txt` - Python dependencies for the application.


### High level overview

Twitter is a firehose of data from which - if used properly - we can learn a lot about social sentiment. There are cases such as with GameStop where attitudes expressed on social media led to huge market changes. If this behavior can be predicted, you have the potential to make a lot of money. Most of the time, you can scroll Twitter for a long time and not glean much insight. With Deephaven and a little bit of natural language processing, we can quickly determine the overall sentiment of a topic to provide a rough idea of the future outlook.

We'll show you how to pull in Twitter data and process that in Deephaven. This data can then be combined with other data - for this post, we chose to look at cryptocurrency, but the possibilities are endless.

## Dependencies

* The [Deephaven-core dependencies](https://github.com/deephaven/deephaven-core#required-dependencies) are required to build and run this project.

## Launch

To launch the latest release, you can clone the repository via:

```shell
git clone https://github.com/deephaven-examples/twitter-sentiment.git
cd twitter-sentiment
```

A start script will install the needed python modules. It will also start the Deephaven IDE.

To run it, execute:

```shell
./twitter-sentiment.sh
```

Running this script will start several Docker containers that work together to launch Deephaven with the needed dependancies. To view the data navigate to [http://localhost:10000/ide](http://localhost:10000/ide).  To view the data you need to edit the `keys.py` file with your infomration.


## Prereqs

[Twitter](https://developer.twitter.com/en/docs/twitter-api) provides an API to make it easy to pull public tweets. In order to use this code as-is, you need to also have a Twitter Developer account and copy your Bearer Token.

```python
import nltk
nltk.download('punkt')
nltk.download('vader_lexicon')

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
```

### Run the program

This program is intended to be fine-tuned to fit your data needs. Below are the values you'll need to change to customize the program for your specific use case and information.

In this example, I perform sentiment analysis on Dogecoin tweets over the course of one week.

1. First, you need the token I mentioned above. Important: the Bearer Token is provided by Twitter and each developer has a monthly limit, so keep this token private.

2. I search for any tweet that contains the term `DOGE`.

3. Since there is a tweet-rate-limit and I want to see the tweets for the last seven days, I collect just 10 tweets for each time pull with `max_results = 10`. I recommend using low numbers for testing. When you are ready for production, increase as needed, while keeping in mind the rate limit.

4. Next, to see how the sentiment of tweets change with time, I divide those seven days up into discreet `time_bins`. More bins will give you the ability to see more refined changes in the social sentement, but would also pull in more tweets, which means you hit your rate limit quicker.

5. My [Twitter access level](https://developer.twitter.com/en/docs/twitter-api/getting-started/about-twitter-api) limits the amount of historical tweets I can pull to seven days, so I set `time_history = 7`. This is the standard for non-academic searches.

```python
# Make sure you enter your token like this 'AAAD...JFH'
bearer_token = '<INPUT YOUR TOKEN HERE>'

# Change this to search whatever term you want on Twitter
search_term = 'DOGE'

# Max results per time bin
max_results = 10

# Time intervals to split data
time_bins = 10

# How many days to go back. Max 7 for non-academic searches
time_history = 7
```

### Configure your functions

In this section of code, we created the functions needed to pull the data from Twitter.

1. Twitter provides a lot of sample code with the v2 API. These functions are pulled from the [Github Twitter-API-v2-sample-code repo](https://github.com/twitterdev/Twitter-API-v2-sample-code) so that we connect to the needed endpoints with the appropriate authorization.

```python
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
```

2. Tweets contain a lot of metadata that can be useful. Here, I set the fields I like to work with: just the `tweet.fields` and `user.fields` data to keep it simple. Using these fields allows me to weigh tweets based on the popularity of the tweet or user and ignores location information. The rest are left for you to add as needed and might be good if you want to limit the search to certain places in the world.

```python
def get_query_params(start_time, end_time):
    return {'query': search_term,
                    'start_time': start_time,
                    'end_time': end_time,
                    'max_results': max_results,
    #                 'expansions': 'author_id,in_reply_to_user_id,geo.place_id',
                    'tweet.fields': 'id,text,author_id,in_reply_to_user_id,geo,conversation_id,created_at,lang,public_metrics,referenced_tweets,reply_settings,source',
                    'user.fields': 'id,name,username,created_at,description,public_metrics,verified',
    #                 'place.fields': 'full_name,id,country,country_code,geo,name,place_type',
                    'next_token': {}}
```

3. Now we have the function that pulls the tweets. I've separated it from the previous code to make it easier to change the `query_params` to the date zone you want.

4. By default, if given a start time range of seven days ago, only recent tweets will be pulled. Since I want a guarantee of dates in bins, I supply the exact start and end date for each request.

5. This function is called for each time bin and returns all the tweet data requested in JSON format.

```python
def get_tweets(query_params):
    headers = create_headers(bearer_token)
    json_response = connect_to_endpoint(search_url, headers, query_params)
    return(json_response['data'])
```

### Clean the tweets

Since I'm performing a sentiment analysis on the content of the tweets, I clean each tweet. This is optional but provides a more uniform appearance to the tweets in the table.

```python
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
```

### Assess sentiment

Next, I run each tweet through the NLTK `SentimentIntensityAnalyzer`. This returns the polarity score of the tweet - that is how positive, negative, and neutral a tweet is, as well as the combined score. Often a tweet will be filled with made up words, acronyms and such. These generally are scored as neutral and do not impact the analysis.

```python
def analyze_line(text):
    sid = SentimentIntensityAnalyzer()
    return(sid.polarity_scores(text))
```

### Put our data in a table

This last function is needed to create a table to store our data.

1. We use Deephaven's [DynamicTableWriter class](https://deephaven.io/core/docs/reference/table-operations/create/DynamicTableWriter/), which calls the function for each iteration of the dynamic table.

2. We add to the table for each `time_bins`.

By formatting the data with [Deephaven Types](https://github.com/deephaven/deephaven-core/blob/main/Integrations/python/deephaven/Types.py), we make it easy to [join](/core/docs/how-to-guides/joins-overview/), [filter](/core/docs/how-to-guides/use-filters/), [summarize](/core/docs/how-to-guides/combined-aggregations/), [plot](/core/docs/how-to-guides/user-interface/chart-builder/) and perform other analysis on our table.

```python
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
```

3. Finally, I create the `tableWriter_sia` and execute the threading to run the above function. This will create a table `sia_data` that fills with the tweets and their metadata, as well as the sentiment of each tweet.

```python
tableWriter_sia = DynamicTableWriter(
    ["Text", "Compound", "Negative", "Neutral", "Positive", "ID", "DateTime", "Retweet_count", "Reply_count", "Like_count", "Quote_count"],
    [dht.string, dht.double, dht.double, dht.double, dht.double, dht.double, dht.datetime, dht.int_, dht.int_, dht.int_, dht.int_])
sia_data = tableWriter_sia.getTable()

thread_sia = threading.Thread(target = thread_func)
thread_sia.start()
```


### Analyze the data

Now the fun part. Let's do some analysis on the tweets so we can see how the search term's positivity and negativity have changed with time.

First, let's aggregate the tweets so that we can get a summary of each tweet inside our chosen time bins.

This code:

1. Creates a series of averages and weighted averages.
2. Creates the `combined_tweets` table that shows us the overall sentiment each minute for our time bins.

```python
from deephaven import Aggregation as agg, as_list

agg_list = as_list([
    agg.AggCount("Count"),
    agg.AggAvg("Average_negative = Negative"),
    agg.AggAvg("Average_neutral = Neutral"),
    agg.AggAvg("Average_positive = Positive"),
    agg.AggAvg("Average_compound = Compound"),
    agg.AggWAvg("Retweet_count", "Weight_negative = Negative"),
    agg.AggWAvg("Retweet_count","Weight_neutral = Neutral"),
    agg.AggWAvg("Retweet_count","Weight_positive = Positive"),
    agg.AggWAvg("Retweet_count","Weight_compound = Compound")
])

from deephaven.DateTimeUtils import expressionToNanos, convertDateTime, upperBin

combined_tweets = sia_data.update("Time_bin = upperBin(DateTime, 10000)").sort("DateTime").aggBy(agg_list,"Time_bin").sort("Time_bin")
```

The table's cool, but not as useful as a plot. I use Deephaven's plotting methods to create a nice visualization of my data.

```python
from deephaven import Plot

sia_averages = Plot.plot("AVG_Neg", combined_tweets, "Time_bin", "Average_negative")\
    .lineColor(Plot.colorRGB(255,0,0,100))\
    .plot("AVG_Pos", combined_tweets, "Time_bin", "Average_positive")\
    .lineColor(Plot.colorRGB(0,255,0,100))\
    .show()
```

## Your turn

This code provides a basic starter. You can use it to make your own searches, tie to other programs, or just see how social media is doing.

We hope this program inspires you. If you make something of your own or have an idea to share, we'd love to hear about it on [Gitter](https://gitter.im/deephaven/deephaven)!



## Related documentation

- [Simple Kafka import](https://deephaven.io/core/docs/how-to-guides/kafka-simple/)
- [Kafka introduction](https://deephaven.io/core/docs/conceptual/kafka-in-deephaven/)
- [How to connect to a Kafka stream](https://deephaven.io/core/docs/how-to-guides/kafka-stream/)
- [Kafka basic terminology](https://deephaven.io/core/docs/conceptual/kafka-basic-terms/)
- [consumeToTable](https://deephaven.io/core/docs/reference/data-import-export/Kafka/consumeToTable/)
