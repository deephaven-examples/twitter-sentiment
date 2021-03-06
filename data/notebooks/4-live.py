coin = 'OKEX:DOGE-ETH'
#seconds between requests
time_to_sleep = 30

#how long to keep listening in minutes
time_alive = 20

max_id = 1510238364283338752
resolution = '1' # Available values: 1, 5, 15, 30, 60, 'D', 'W', 'M'

#twitter paramters for live tweets
def get_query_params_live(search_term, max_id):
    return {'query': search_term,
                    'since_id': max_id,
                    'max_results': max_results,
                    'tweet.fields': 'id,text,author_id,in_reply_to_user_id,geo,conversation_id,created_at,lang,public_metrics,referenced_tweets,reply_settings,source',
                    'user.fields': 'id,name,username,created_at,description,public_metrics,verified',
                    'next_token': {}}

resolution = '1' # Available values: 1, 5, 15, 30, 60, 'D', 'W', 'M'

def write_data(all_text):
    data = finnhub_client.crypto_candles(coin, resolution, int(millis(minus_period(now(),to_period("T"+str(int((24*time_history)))+"H")))/1000), int(datetime.timestamp(datetime.now())))
    if data['s'] =='ok' and len(data['s'])>0 and  data['c'] != None and  len(data['c'])>0:
        c_live = data['c'][0]
        h_live  = data['h'][0]
        l_live  = data['l'][0]
        o_live  = data['o'][0]
        v_live  = data['v'][0]
        global max_id
        i = 0
        for t in all_text:
            id_live = int(t['id'])
            try:
                if float(t['id'])!=None and max_id < float(t['id']):
                    globals()['max_id'] = int(t['id'])
                combined_live  = analyze_line(cleanText(t['text']))
                negative_live  = 100*combined_live.get('neg')
                neutral_live  = 100*combined_live.get('neu')
                compound_live  = 100*combined_live.get('compound')
                positive_live  = 100*combined_live.get('pos')
                dateTime_live  = t['created_at'][:-1]+" NY"
                retweet_count_live    = t['public_metrics']['retweet_count']
                text_live  = t['text'].split('\n', 1)[0]
                tableWriter_live.write_row(t['text'], float(compound_live), float(negative_live), float(neutral_live), float(positive_live),to_datetime(dateTime_live), int(retweet_count_live), float(c_live), float(h_live), float(l_live), float(o_live), float(v_live))
                i = i + 1
            except:
                print('error/NoneType')
        print("finished writing rows: ", i)
        return max_id

def thread_func_live():
    global max_id
    for i in range(0, time_alive*60, time_to_sleep):
        query_params = get_query_params_live(search_term, max_id)
        all_text = get_tweets(query_params)
        max_id = write_data(all_text)
        time.sleep(time_to_sleep)

tableWriter_live = DynamicTableWriter(
    {"Text":dht.string, "Compound":dht.double, "Negative":dht.double, "Neutral":dht.double, "Positive":dht.double,  "DateTime":dht.DateTime, "Retweet_count":dht.int_, "Close":dht.float64, "High":dht.float64, "Low":dht.float64, "Open":dht.float64, "Volume":dht.float64})
thread_live = Thread(target=thread_func_live)
thread_live.start()
live_data = tableWriter_live.table