# TD Ameritrade API Equity Price History Data

from datetime import datetime

import pandas as pd
import pytz

from ..auth import get_token, get_content


# GET price history for a symbol
class PriceHistory:
    def __init__(self, ticker: str = None):
        self.ticker = ticker.upper()
        self.token = get_token()

    def price_history(self,
                      period: int = 1,
                      period_type: str = 'year',
                      frequency: int = 1,
                      frequency_type: str = 'daily',
                      ext: str = 'false'
                      ):

        # Check if parameters are correct:
        if period_type not in ['year', 'day', 'month', 'ytd']:
            raise ValueError("period_type invalid. Accepted valued: 'year', 'day', 'month', 'ytd'")
        if frequency_type not in ['daily', 'weekly', 'monthly', 'minute']:
            raise ValueError("frequency_type invalid. Accepted values: 'daily', 'weekly', 'monthly', 'minute'")

        # API endpoint
        endpoint = r'https://api.tdameritrade.com/v1/marketdata/{}/pricehistory'.format(self.ticker)

        params = {'periodType': period_type,
                  'period': period,
                  'frequencyType': frequency_type,
                  'frequency': frequency}

        if frequency_type == 'minute':
            params.update({'needExtendedHoursData': ext})

        # GET data
        content = get_content(url=endpoint, params=params, headers=self.token)
        response = content.json()
        df = pd.json_normalize(response['candles'])

        # Rename datetime as unix
        df.rename(columns={'datetime': 'unix'}, inplace=True)

        # Convert unix to datetime
        if frequency_type == 'minute':
            df['datetime'] = df.apply(lambda row: datetime.fromtimestamp(row.unix / 1000)
                                      .astimezone(tz=pytz.timezone("US/Eastern")).strftime('%Y-%m-%d %H:%M:%S'),
                                      axis=1)
        else:
            df['datetime'] = df.apply(lambda row: datetime.utcfromtimestamp(row.unix / 1000).strftime('%Y-%m-%d'),
                                      axis=1)

        # Format df
        df = df[['datetime', 'open', 'high', 'low', 'close', 'volume']].copy()
        df.set_index('datetime', inplace=True)

        return df

    # GET the daily price history
    def daily(self, period: int = 20):
        df = self.price_history(period=period, period_type='year', frequency_type='daily', frequency=1)
        return df

    def minute(self, period: int = 10, ext: str = 'false'):
        df = self.price_history(period=period, period_type='day', frequency_type='minute', frequency=1, ext=ext)
        return df
