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

table = sia_datav3.update("Timestamp=convertDateTime(DateTime)", "Time_bin = upperBin(Timestamp, 10000)").sort("Timestamp")
combined_tweets = table.aggBy(agg_list,"Time_bin").sort("Time_bin")



from deephaven import Plot

sia_averages = Plot.plot("AVG_Neg", combined_tweets, "Time_bin", "Average_negative")\
    .lineColor(Plot.colorRGB(255,0,0,100))\
    .plot("AVG_Pos", combined_tweets, "Time_bin", "Average_positive")\
    .lineColor(Plot.colorRGB(0,255,0,100))\
    .show()

sia_weighted_averages = Plot.plot("Weight_Neg", combined_tweets, "Time_bin", "Weight_negative")\
    .lineColor(Plot.colorRGB(255,0,0,100))\
    .plot("Weight_Pos", combined_tweets, "Time_bin", "Weight_positive")\
    .lineColor(Plot.colorRGB(0,255,0,100))\
    .twinX()\

coins_ohlc = Plot.ohlcPlot("coins", coin_data.where("Close >10"), "DateTime", "Open", "High", "Low", "Close")\
    .show()


