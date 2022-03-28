from deephaven import Aggregation as agg, as_list
from deephaven.DateTimeUtils import expressionToNanos, convertDateTime, lowerBin, upperBin

agg_list_tweets = as_list([
    agg.AggCount("Count_tweet"),
    agg.AggAvg("Average_negative = Negative"),
    agg.AggAvg("Average_neutral = Neutral"),
    agg.AggAvg("Average_positive = Positive"),
    agg.AggAvg("Average_compound = Compound"),
    agg.AggWAvg("Retweet_count", "Weight_negative = Negative"),
    agg.AggWAvg("Retweet_count","Weight_neutral = Neutral"),
    agg.AggWAvg("Retweet_count","Weight_positive = Positive"),
    agg.AggWAvg("Retweet_count","Weight_compound = Compound")
])

agg_list_coins = as_list([
    agg.AggCount("Count_coin"),
    agg.AggAvg("Average_close = Close"),
    agg.AggAvg("Average_high = High"),
    agg.AggAvg("Average_low = Low"),
    agg.AggAvg("Average_open = Open"),
])

nanosBin = expressionToNanos("T10M")

agged_tweet_data = sia_data.update("Time_bin = upperBin(DateTime,nanosBin)")
combined_tweets = agged_tweet_data.aggBy(agg_list_tweets,"Time_bin").sort("Time_bin")

agged_coin_data = coin_data.update("Time_bin = upperBin(DateTime,nanosBin)")
combined_coins = agged_coin_data.aggBy(agg_list_coins,"Time_bin").sort("Time_bin")

combined_data = combined_tweets.aj(combined_coins,"Time_bin").update("Average_negative=Average_negative*-100", "Weight_compound=Weight_compound*100", "Average_positive =100* Average_positive" )
