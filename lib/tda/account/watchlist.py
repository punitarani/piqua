# TD Ameritrade API Account data

import pandas as pd

from config import account_id
from ..auth import get_token, get_content


# Watchlist Data
class Watchlist:
    def __init__(self):
        self.token = get_token()
        self.accountID = account_id

    # GET all watchlists for an account
    def watchlists(self):
        endpoint = r'https://api.tdameritrade.com/v1/accounts/{}/watchlists'.format(self.accountID)
        content = get_content(url=endpoint, headers=self.token)
        response = content.json()
        watchlists = {}
        for watchlist in response:
            df = pd.json_normalize(watchlist['watchlistItems'])
            symbols = df['instrument.symbol'].tolist()

            watchlists.update({watchlist['name']: symbols})

        return watchlists
