# TD Ameritrade API Option Chain data

import statistics
from datetime import datetime

import pandas as pd

from ..auth import get_token, get_content


# Get Unix Epoch time
def get_unix_time(dt):
    # grab the starting point, so time '0'
    epoch = datetime.utcfromtimestamp(0)

    return (dt - epoch).total_seconds() * 1000.0


# Option Chain Data
class OptionChain:
    def __init__(self, ticker: str):
        self.ticker = ticker
        self.token = get_token()
        self.underlyingData = None

    @staticmethod
    def oc_json_to_df(oc_json, exclude_weekly=False, expiration=None):
        response = oc_json

        # Split the json to puts and calls data
        puts = response['putExpDateMap']
        calls = response['callExpDateMap']

        # Identify if json is put and/or call
        pcs = []
        if calls != {}:
            pcs.append('callExpDateMap')
        if puts != {}:
            pcs.append('putExpDateMap')

        # Get the expiration dates
        expiration_dates = []
        if exclude_weekly:
            for exp_put in puts.keys():
                if exp_put in calls.keys():
                    strike_0 = list(puts[exp_put].keys())[0]
                    if 'Weekly' not in puts[exp_put][strike_0][0]['description']:
                        expiration_dates.append(exp_put)
        else:
            expiration_dates = [exp_put for exp_put in puts.keys() if exp_put in calls.keys()]

        # Filter expiration
        if expiration is not None:
            expiration_dates = [exp for exp in expiration_dates if expiration in exp]

        # Get the strikes for each expiration date
        strikes_dict = {}
        for exp_date in expiration_dates:
            strikes = [strike for strike in puts[exp_date].keys() if strike in calls[exp_date].keys()]
            strikes_dict.update({exp_date: strikes})

        # Iterate through the OC JSON and map values to df
        data = []
        for pc in pcs:
            for expDate in expiration_dates:
                for strike in strikes_dict[expDate]:
                    data.append(response[pc][expDate][strike][0])

        # Create OC DataFrame
        df = pd.DataFrame(data)

        # Convert expiration date from timestamp to string YYYY-MM-DD
        df['expirationDate'] = df['expirationDate'].values.astype(dtype='datetime64[ms]')
        df['expirationDate'] = df['expirationDate'].astype(str).str[:10]

        # Index df
        df_index = ['expirationDate', 'putCall', 'strikePrice']
        df.set_index(df_index, inplace=True)

        return df

    # GET option chain for an optionable Symbol
    def chain(self, contract_type='ALL', include_quotes=True, exp_month='ALL', option_type='S', exclude_weekly=False,
              option_range='ALL'):
        endpoint = r'https://api.tdameritrade.com/v1/marketdata/chains'
        params = {'symbol': self.ticker,
                  'contractType': contract_type,
                  'includeQuotes': include_quotes,
                  'expMonth': exp_month,
                  'optionType': option_type,
                  'range': option_range}
        content = get_content(url=endpoint, params=params, headers=self.token)
        response = content.json()

        self.underlyingData = response['underlying']

        df = self.oc_json_to_df(oc_json=response, exclude_weekly=exclude_weekly)

        return df

    # Get best option chain near desired expiration
    def chain_best(self, dte=45, exclude_weekly=True):
        endpoint = r'https://api.tdameritrade.com/v1/marketdata/chains'
        params = {'symbol': self.ticker,
                  'contractType': 'ALL',
                  'includeQuotes': True,
                  'expMonth': 'ALL',
                  'optionType': 'S'}
        content = get_content(url=endpoint, params=params, headers=self.token)
        response = content.json()

        self.underlyingData = response['underlying']

        # get best expiration
        exp = self.calculate_closest_expiration(oc_json=response, dte=dte, dte_min=21, dte_max=65,
                                                dte_min_diff=5, exclude_weekly=True)

        df = self.oc_json_to_df(oc_json=response, exclude_weekly=exclude_weekly, expiration=exp)

        return df

    # Calculate closest expiration
    @staticmethod
    def calculate_closest_expiration(oc_json, dte: int, dte_min_diff: int, dte_min: int, dte_max: int,
                                     exclude_weekly=True, condition='last'):
        response = oc_json

        # Split the json to puts and calls data
        puts = response['putExpDateMap']
        calls = response['callExpDateMap']

        # Get the expiration dates
        expiration_dates = {}
        for exp in puts.keys():
            if exp in calls.keys():
                if exclude_weekly and 'weekly' in puts[exp][list(puts[exp].keys())[0]][0]['description'].lower():
                    continue
                else:
                    exp_date = exp.split(':')[0]
                    days_to_exp = int(exp.split(':')[-1])
                    distance = days_to_exp - dte

                    # Filter dte params
                    if dte_min <= days_to_exp <= dte_max and days_to_exp - dte_min >= dte_min_diff:
                        expiration_dates.update({exp_date: abs(distance)})

        # Get the closest expiration dates
        closest_distance = min(expiration_dates.values())
        closest_dates = {k: v for k, v in expiration_dates.items() if v == closest_distance}

        if condition == 'last':
            return list(closest_dates.keys())[-1]
        else:
            return list(closest_dates.keys())[0]

    # Get closest expiration to given days to expiration
    def get_closest_expiration(self, dte=45, exclude_weekly=True, dte_min_diff=5, dte_min=21, dte_max=120,
                               condition='last'):
        # Input Params Definitions
        """
        dte = target days to expiration
        exclude_weekly = only include non-weekly expirations
        dte_min_diff = minimum days to dte_min
        dte_min = minimum days to expiration
        dte_max = maximum days to expiration
        condition = last expiration or first expiration if multiple found
        """

        endpoint = r'https://api.tdameritrade.com/v1/marketdata/chains'
        params = {'symbol': self.ticker}
        content = get_content(url=endpoint, params=params, headers=self.token)
        response = content.json()

        closest_date = self.calculate_closest_expiration(oc_json=response, dte=dte, dte_min=dte_min, dte_max=dte_max,
                                                         dte_min_diff=dte_min_diff, exclude_weekly=exclude_weekly,
                                                         condition=condition)

        return closest_date

    # Calculate the implied volatility of a stock for all expirations
    def calculate_impl_vol(self):
        oc = self.chain()

        # Get the expiration dates
        expiration_dates = list(set([row[0] for row in oc.index.tolist()]))

        # {expiration: IV}
        iv_dict = {}

        # Calculate IV
        for exp in expiration_dates:
            exp_df = oc.loc[exp][['delta', 'volatility']]
            strikes = list(set([row[-1] for row in exp_df.index.tolist()]))
            strikes.sort()

            # Filter df
            calls = exp_df.loc['CALL']
            puts = exp_df.loc['PUT']

            # Remove rows with missing IV
            calls = calls[calls['delta'] != 'NaN']
            puts = puts[puts['delta'] != 'NaN']

            # Filter by delta 0.1-0.9
            calls = calls[calls['delta'].between(0.1, 0.9)]
            puts = puts[puts['delta'].between(-0.9, -0.1)]

            # Delta weight
            calls_weight = [delta / sum(calls.delta.tolist()) for delta in calls.delta.tolist()]
            puts_weight = [delta / sum(puts.delta.tolist()) for delta in puts.delta.tolist()]

            # Equal weight
            # calls_weight = np.ones(len(calls))/len(calls)
            # puts_weight = np.ones(len(puts))/len(puts)

            # Calculate IV
            call_iv = sum([calls.iloc[i].loc['volatility'] * calls_weight[i] for i in range(len(calls))])
            put_iv = sum([puts.iloc[i].loc['volatility'] * puts_weight[i] for i in range(len(puts))])

            iv = round(statistics.mean([call_iv, put_iv]), 2)

            iv_dict.update({exp: iv})

        # Convert dict to df
        iv_df = pd.json_normalize(iv_dict).T
        iv_df.rename(columns={0: 'iv'}, inplace=True)
        iv_df = iv_df.sort_index(ascending=True)

        return iv_df
