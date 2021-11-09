# TD Ameritrade API Account data

import pandas as pd

from config import account_id
from ..auth import get_token, get_content


# Account Data
class Account:
    def __init__(self):
        self.token = get_token()
        self.accountID = account_id

    # GET User Principal details.
    def user_principals(self):
        endpoint = r'https://api.tdameritrade.com/v1/userprincipals'
        params = {'fields': 'streamerSubscriptionKeys,streamerConnectionInfo,preferences,surrogateIds'}
        content = get_content(url=endpoint, params=params, headers=self.token)
        response = content.json()
        df = pd.json_normalize(response).T
        return df

    # Account balances for a specific account.
    def balances(self):
        endpoint = r'https://api.tdameritrade.com/v1/accounts/{}'.format(self.accountID)
        content = get_content(url=endpoint, headers=self.token)
        response = content.json()['securitiesAccount']
        df = pd.json_normalize(response).T
        return df

    # Account positions for a specific account.
    def positions(self):
        endpoint = r'https://api.tdameritrade.com/v1/accounts/{}'.format(self.accountID)
        params = {'fields': 'positions'}
        content = get_content(url=endpoint, params=params, headers=self.token)
        response = content.json()['securitiesAccount']['positions']
        df = pd.json_normalize(response).set_index('instrument.symbol')

        cols = ['longQuantity', 'shortQuantity', 'settledLongQuantity', 'settledShortQuantity', 'averagePrice',
                'marketValue', 'currentDayProfitLoss', 'currentDayProfitLossPercentage', 'maintenanceRequirement',
                'currentDayCost', 'previousSessionLongQuantity', 'previousSessionShortQuantity',
                'instrument.assetType', 'instrument.cusip', 'instrument.description', 'instrument.putCall',
                'instrument.underlyingSymbol']

        df = df.reindex(columns=cols)

        return df

    # Account Transactions
    def transactions(self, symbol=None):
        endpoint = r'https://api.tdameritrade.com/v1/accounts/{}/transactions'.format(self.accountID)
        params = {}
        if symbol is not None:
            params.update({'symbol': symbol.upper()})
        content = get_content(url=endpoint, params=params, headers=self.token)
        response = content.json()
        df = pd.json_normalize(response)
        df.set_index('transactionId', inplace=True)
        return df

    # Account orders for a specific account.
    def orders(self):
        endpoint = r'https://api.tdameritrade.com/v1/accounts/{}'.format(self.accountID)
        params = {'fields': 'orders'}
        content = get_content(url=endpoint, params=params, headers=self.token)
        response = content.json()['securitiesAccount']['orderStrategies']
        df = pd.json_normalize(response)
        # TODO: Fix df indexing
        return df
