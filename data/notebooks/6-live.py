coin = 'COINBASE:DOGE-USD'
#seconds between requests
time_to_sleep = 60

#how long to keep listening in minutes
time_alive = 1
for max_id in (sia_data.maxBy().update("ID=ID").selectDistinct("ID").getColumn("ID").getDirect()):
    max_id = (int(max_id))
    globals()[max_id] = max_id

resolution = '1' # Available values: 1, 5, 15, 30, 60, 'D', 'W', 'M'

#twitter paramters for live tweets
def get_query_params_live(search_term, max_id):
    return {'query': search_term,
                    'since_id': max_id,
                    'max_results': max_results,
                    'tweet.fields': 'id,text,author_id,in_reply_to_user_id,geo,conversation_id,created_at,lang,public_metrics,referenced_tweets,reply_settings,source',
                    'user.fields': 'id,name,username,created_at,description,public_metrics,verified',
                    'next_token': {}}


def write_data(all_text, tableWriter):
    data = finnhub_client.crypto_candles(coin, resolution, int(millis(minus(currentTime(),convertPeriod("T"+str(int(1))+"M")))/1000), int(millis(currentTime())/1000))
    if data['s'] =='ok' and len(data['s'])>0 and  data['c'] != None and  len(data['c'])>0:
        c = data['c'][0]
        h = data['h'][0]
        l = data['l'][0]
        o = data['o'][0]
        v = data['v'][0]
        global max_id
        i = 0
        for t in all_text:
            id = int(t['id'])
            if max_id < float(t['id']):
                globals()['max_id'] = int(t['id'])
            combined = analyze_line(cleanText(t['text']))
            negative = combined.get('neg')
            neutral = combined.get('neu')
            compound = combined.get('compound')
            positive = combined.get('pos')
            dateTime = t['created_at'][:-1]+" NY"
            retweet_count   = t['public_metrics']['retweet_count']
            tableWriter.logRowPermissive(t['text'], float(compound), float(negative), float(neutral), float(positive), float(id),convertDateTime(dateTime), int(retweet_count),coin, float(c), float(h), float(l), float(o), float(v) )
            i = i + 1
        print("finished writing rows: ", i)
        return max_id

def thread_func(search_term, tableWriter):
    global max_id
    for i in range(0, time_alive*60, time_to_sleep):
        query_params = get_query_params_live(search_term, max_id)
        all_text = get_tweets(query_params)
        max_id = write_data(all_text, tableWriter)
        time.sleep(time_to_sleep)

def make_table(term):
    tableWriter = DynamicTableWriter( 
        ["Text", "Compound", "Negative", "Neutral", "Positive", "ID", "DateTime", "Retweet_count",  "Coin", "Close", "High", "Low", "Open", "Volume"],
        [dht.string, dht.double, dht.double, dht.double, dht.double, dht.double, dht.datetime, dht.int_,dht.string, dht.float64, dht.float64, dht.float64, dht.float64, dht.float64])
    thread = threading.Thread(target=thread_func, args=[term, tableWriter])
    thread.start()
    return tableWriter.getTable()

live_data= make_table(search_term)
