# TD Ameritrade API Equity data

import pandas as pd

from ..auth import get_token, get_content


# Equity(Stock) Data
class Equity:
    def __init__(self, ticker):
        self.token = get_token()

        if isinstance(ticker, str):
            self.ticker = ticker.upper()
            self.tickers = [self.ticker]
        elif isinstance(ticker, list):
            self.ticker = ticker[0].upper()
            self.tickers = [t.upper() for t in ticker]
        elif isinstance(ticker, int):
            self.cusip = ticker

    def mark(self):
        endpoint = r'https://api.tdameritrade.com/v1/marketdata/{}/quotes'.format(self.ticker)
        content = get_content(url=endpoint, headers=self.token)
        response = content.json()
        mark = response[self.ticker]['mark']
        return mark

    # Get quote for a symbol
    def quote(self):
        endpoint = r'https://api.tdameritrade.com/v1/marketdata/{}/quotes'.format(self.ticker)
        content = get_content(url=endpoint, headers=self.token)
        response = content.json()
        df = pd.DataFrame.from_dict(response)
        return df

    # Get quote for one or more symbols
    def quotes(self):
        endpoint = r'https://api.tdameritrade.com/v1/marketdata/quotes'
        params = {'symbol': ','.join(self.tickers)}
        content = get_content(url=endpoint, params=params, headers=self.token)
        response = content.json()
        df = pd.DataFrame.from_dict(response)
        return df

    # Retrieve fundamental data.
    def fundamentals(self):
        endpoint = r'https://api.tdameritrade.com/v1/instruments'
        params = {'symbol': self.tickers, 'projection': 'fundamental'}
        content = get_content(url=endpoint, params=params, headers=self.token)
        response = content.json()
        df = pd.DataFrame()
        for ticker in self.tickers:
            response_ticker = response[ticker]['fundamental']
            df_ticker = pd.json_normalize(response_ticker)
            df_ticker = df_ticker.set_index('symbol').T
            df = pd.concat([df, df_ticker], axis=1, join='outer')
        return df
