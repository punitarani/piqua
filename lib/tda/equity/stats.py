# TD Ameritrade API Equity Stats Data

import numpy as np
import pandas as pd

from ..equity import Equity
from ..equity import PriceHistory


class Stats:
    def __init__(self, ticker):
        self.ticker = ticker.upper()

    # Calculate the beta of a stock
    def beta(self, period: int = 1, index: str = 'SPY', direction_filter: bool = None):
        # Get price history data of ticker and index
        index_df = PriceHistory(ticker=index).price_history(period=period, period_type='year',
                                                            frequency=1, frequency_type='daily')
        ticker_df = PriceHistory(ticker=self.ticker).price_history(period=period, period_type='year', frequency=1,
                                                                   frequency_type='daily')

        # Calculate daily returns
        index_df = index_df.assign(i=(index_df['close'] - index_df['open']) / index_df['open'])
        ticker_df = ticker_df.assign(t=(ticker_df['close'] - ticker_df['open']) / ticker_df['open'])
        returns_df = pd.merge(index_df.i, ticker_df.t, left_index=True, right_index=True)

        # Filter direction (up/down: True/False)
        if direction_filter is not None and direction_filter:
            returns_df = returns_df[returns_df.i > 0]
        elif direction_filter is not None and not direction_filter:
            returns_df = returns_df[returns_df.i < 0]

        # Calculate beta
        covariance = returns_df.cov().loc['t', 'i']
        variance = returns_df.var()['i']
        beta = round(covariance / variance, 3)

        return beta

    # Calculate the correlation
    def correlation(self, period: int = 1, index: str = 'SPY', direction_filter: bool = None):
        # Get price history data of ticker and index
        index_df = PriceHistory(ticker=index).price_history(period=period, period_type='year',
                                                            frequency=1, frequency_type='daily')
        ticker_df = PriceHistory(ticker=self.ticker).price_history(period=period, period_type='year', frequency=1,
                                                                   frequency_type='daily')

        # Calculate daily returns
        index_close = index_df.close.to_list()
        ticker_close = ticker_df.close.to_list()

        index_returns = []
        ticker_returns = []

        for i in range(1, min([len(index_close), len(ticker_close)])):
            index_returns.append((index_close[i] - index_close[i - 1]) / index_close[i - 1])
            ticker_returns.append((ticker_close[i] - ticker_close[i - 1]) / ticker_close[i - 1])

        # Filter direction (up/down: True/False)
        if direction_filter is not None and direction_filter:
            index = 0
            for i in index_returns:
                if i < 0:
                    index_returns.pop(index)
                    ticker_returns.pop(index)
                    index += 1
        elif direction_filter is not None and not direction_filter:
            index = 0
            for i in index_returns:
                if i > 0:
                    index_returns.pop(index)
                    ticker_returns.pop(index)
                    index += 1

        # Calculate Correlation
        correlation = round(np.corrcoef(ticker_returns, index_returns)[0, 1], 3)

        return correlation

    # Calculate the probability move
    def volatility(self):
        quote = Equity(ticker=self.ticker).quote()
        volatility = quote.loc['volatility', self.ticker]

        return volatility
