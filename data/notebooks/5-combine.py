from deephaven import Aggregation as agg, as_list
from deephaven.DateTimeUtils import expressionToNanos, convertDateTime, lowerBin, upperBin
import deephaven.Types as dht
from deephaven.conversion_utils import NULL_DOUBLE

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

agg_list_combined = as_list([
    agg.AggCount("Count_tweet"),
    agg.AggAvg("Average_negative = Negative"),
    agg.AggAvg("Average_neutral = Neutral"),
    agg.AggAvg("Average_positive = Positive"),
    agg.AggAvg("Average_compound = Compound"),
    agg.AggWAvg("Retweet_count", "Weight_negative = Negative"),
    agg.AggWAvg("Retweet_count","Weight_neutral = Neutral"),
    agg.AggWAvg("Retweet_count","Weight_positive = Positive"),
    agg.AggWAvg("Retweet_count","Weight_compound = Compound"),
    agg.AggCount("Count_coin"),
    agg.AggAvg("Average_close = Close"),
    agg.AggAvg("Average_high = High"),
    agg.AggAvg("Average_low = Low"),
    agg.AggAvg("Average_open = Open"),
])

nanosBin = expressionToNanos("T1M")

combined_tweets = sia_data.update("Time_bin = (DateTime)lowerBin(DateTime,nanosBin)")\
                    .aggBy(agg_list_tweets,"Time_bin").where("Weight_negative <100","Weight_negative>-100" )\

combined_coins = coin_data.update("Time_bin = (DateTime)upperBin(DateTime,nanosBin)")\
                    .aggBy(agg_list_coins,"Time_bin")\

combined_data = combined_tweets.aj(combined_coins,"Time_bin")\
                    .sortDescending("Time_bin")

live_binned = live_data.update("Time_bin = (DateTime)upperBin(DateTime,nanosBin)")\
                    .aggBy(agg_list_combined,"Time_bin")\
                    .sortDescending("Time_bin")