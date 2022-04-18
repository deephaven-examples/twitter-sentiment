from deephaven import agg as agg
from deephaven.time import to_datetime, now, plus_period, to_period, lower_bin, to_nanos
import deephaven.dtypes as dht
from deephaven.constants import NULL_DOUBLE


agg_list_tweets = [
    agg.count_("Count_tweet"),
    agg.avg(["Average_negative = Negative"]),
    agg.avg(["Average_neutral = Neutral"]),
    agg.avg(["Average_positive = Positive"]),
    agg.avg(["Average_compound = Compound"]),
    agg.weighted_avg("Retweet_count", ["Weight_negative = Negative"]),
    agg.weighted_avg("Retweet_count",["Weight_neutral = Neutral"]),
    agg.weighted_avg("Retweet_count",["Weight_positive = Positive"]),
    agg.weighted_avg("Retweet_count",["Weight_compound = Compound"])
]
agg_list_coins = [
    agg.count_("Count_coin"),
    agg.avg(["Average_close = Close"]),
    agg.avg(["Average_high = High"]),
    agg.avg(["Average_low = Low"]),
    agg.avg(["Average_open = Open"])
]

agg_list_combined = [
    agg.count_("Count_tweet"),
    agg.avg(["Average_negative = Negative"]),
    agg.avg(["Average_neutral = Neutral"]),
    agg.avg(["Average_positive = Positive"]),
    agg.avg(["Average_compound = Compound"]),
    agg.weighted_avg("Retweet_count", ["Weight_negative = Negative"]),
    agg.weighted_avg("Retweet_count",["Weight_neutral = Neutral"]),
    agg.weighted_avg("Retweet_count",["Weight_positive = Positive"]),
    agg.weighted_avg("Retweet_count",["Weight_compound = Compound"]),
    agg.count_("Count_coin"),
    agg.avg(["Average_close = Close"]),
    agg.avg(["Average_high = High"]),
    agg.avg(["Average_low = Low"]),
    agg.avg(["Average_open = Open"])
]

nanosBin = to_nanos("00:01:00")

combined_tweets = sia_data.update(["Time_bin = (DateTime)lower_bin(DateTime,nanosBin)"])\
                    .agg_by(agg_list_tweets,["Time_bin"]).where(["Weight_negative <100","Weight_negative>-100"])\

combined_coins = coin_data.update(["Time_bin = (DateTime)upperBin(DateTime,nanosBin)"])\
                    .agg_by(agg_list_coins,["Time_bin"])\

combined_data = combined_tweets.aj(combined_coins,["Time_bin"])\
                    .sort_descending(["Time_bin"])

live_binned = live_data.update(["Time_bin = (DateTime)upperBin(DateTime,nanosBin)"])\
                    .agg_by(agg_list_combined,["Time_bin"])\
                    .sort_descending(["Time_bin"])