def installations():
    import nltk
    nltk.download('punkt')
    nltk.download('vader_lexicon')

installations()


bearer_token = '<INPUT YOUR TOKEN HERE>'

import finnhub
finnhub_client = finnhub.Client(api_key='<INPUT YOUR KEY HERE>')


search_term = 'DOGE'