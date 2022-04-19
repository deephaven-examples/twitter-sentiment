from deephaven.time import millis_to_datetime, millis

def pull_coins():
    exchanges = finnhub_client.crypto_exchanges()
    temp_ids = []
    for exchange in exchanges:
        long_list = finnhub_client.crypto_symbols(exchange)
        symbols = pd.DataFrame(long_list).loc[:,'symbol']
        temp_ids.append(symbols.values.tolist())

    ids = [item for sublist in temp_ids for item in sublist]

    r=re.compile(".*({}).*".format(search_term))
    return list(filter(r.match, ids))[12:]

ids = pull_coins()

resolution = '5' # Available values: 1, 5, 15, 30, 60, 'D', 'W', 'M'

coin = 'BINANCE:DOGEAUD'

def thread_func_coin():
    data = finnhub_client.crypto_candles(coin, resolution, int(millis(minus_period(now(),to_period("T"+str(int((24*time_history)))+"H")))/1000), int(datetime.timestamp(datetime.now())))
    if data['s'] =='ok' and len(data['s'])>0:
        c = data['c']
        h = data['h']
        l = data['l']
        o = data['o']
        t = data['t']
        v = data['v']
        if c != None:
            for i in range(len(c)):
                tableWriter_coin.write_row(coin, float(c[i]), float(h[i]), float(l[i]), float(o[i]), millis_to_datetime(t[i]*1000), float(v[i]))


tableWriter_coin = DynamicTableWriter(
    {"Coin":dht.string, "Close":dht.float64, "High":dht.float64, "Low":dht.float64, "Open":dht.float64, "DateTime":dht.DateTime, "Volume":dht.float64}
)

coin_data = tableWriter_coin.table
thread_coin = Thread(target = thread_func_coin)
thread_coin.start()