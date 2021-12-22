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
    """Index: ['userId', 'userCdDomainId', 'primaryAccountId', 'lastLoginTime', 'tokenExpirationTime', 'loginTime', 
    'accessLevel', 'stalePassword', 'professionalStatus', 'accounts', 'streamerInfo.streamerBinaryUrl', 
    'streamerInfo.streamerSocketUrl', 'streamerInfo.token', 'streamerInfo.tokenTimestamp', 'streamerInfo.userGroup', 
    'streamerInfo.accessLevel', 'streamerInfo.acl', 'streamerInfo.appId', 'quotes.isNyseDelayed', 
    'quotes.isNasdaqDelayed', 'quotes.isOpraDelayed', 'quotes.isAmexDelayed', 'quotes.isCmeDelayed', 
    'quotes.isIceDelayed', 'quotes.isForexDelayed', 'streamerSubscriptionKeys.keys', 
    'exchangeAgreements.NYSE_EXCHANGE_AGREEMENT', 'exchangeAgreements.NASDAQ_EXCHANGE_AGREEMENT', 
    'exchangeAgreements.OPRA_EXCHANGE_AGREEMENT']"""

    # Columns: [0]
    def user_principals(self) -> pd.DataFrame:
        endpoint = r'https://api.tdameritrade.com/v1/userprincipals'
        params = {'fields': 'streamerSubscriptionKeys,streamerConnectionInfo,preferences,surrogateIds'}
        content = get_content(url=endpoint, params=params, headers=self.token)
        response = content.json()
        df = pd.json_normalize(response).T
        return df

    # Get Account balances for a specific account.
    # Columns:
    """['type', 'accountId', 'roundTrips', 'isDayTrader', 'isClosingOnlyRestricted', 
    'initialBalances.accruedInterest', 'initialBalances.availableFundsNonMarginableTrade', 
    'initialBalances.bondValue', 'initialBalances.buyingPower', 'initialBalances.cashBalance', 
    'initialBalances.cashAvailableForTrading', 'initialBalances.cashReceipts', 
    'initialBalances.dayTradingBuyingPower', 'initialBalances.dayTradingBuyingPowerCall', 
    'initialBalances.dayTradingEquityCall', 'initialBalances.equity', 'initialBalances.equityPercentage', 
    'initialBalances.liquidationValue', 'initialBalances.longMarginValue', 'initialBalances.longOptionMarketValue', 
    'initialBalances.longStockValue', 'initialBalances.maintenanceCall', 'initialBalances.maintenanceRequirement', 
    'initialBalances.margin', 'initialBalances.marginEquity', 'initialBalances.moneyMarketFund', 
    'initialBalances.mutualFundValue', 'initialBalances.regTCall', 'initialBalances.shortMarginValue', 
    'initialBalances.shortOptionMarketValue', 'initialBalances.shortStockValue', 'initialBalances.totalCash', 
    'initialBalances.isInCall', 'initialBalances.pendingDeposits', 'initialBalances.marginBalance', 
    'initialBalances.shortBalance', 'initialBalances.accountValue', 'currentBalances.accruedInterest', 
    'currentBalances.cashBalance', 'currentBalances.cashReceipts', 'currentBalances.longOptionMarketValue', 
    'currentBalances.liquidationValue', 'currentBalances.longMarketValue', 'currentBalances.moneyMarketFund', 
    'currentBalances.savings', 'currentBalances.shortMarketValue', 'currentBalances.pendingDeposits', 
    'currentBalances.availableFunds', 'currentBalances.availableFundsNonMarginableTrade', 
    'currentBalances.buyingPower', 'currentBalances.buyingPowerNonMarginableTrade', 
    'currentBalances.dayTradingBuyingPower', 'currentBalances.equity', 'currentBalances.equityPercentage', 
    'currentBalances.longMarginValue', 'currentBalances.maintenanceCall', 'currentBalances.maintenanceRequirement', 
    'currentBalances.marginBalance', 'currentBalances.regTCall', 'currentBalances.shortBalance', 
    'currentBalances.shortMarginValue', 'currentBalances.shortOptionMarketValue', 'currentBalances.sma', 
    'currentBalances.mutualFundValue', 'currentBalances.bondValue', 'projectedBalances.availableFunds', 
    'projectedBalances.availableFundsNonMarginableTrade', 'projectedBalances.buyingPower', 
    'projectedBalances.dayTradingBuyingPower', 'projectedBalances.dayTradingBuyingPowerCall', 
    'projectedBalances.maintenanceCall', 'projectedBalances.regTCall', 'projectedBalances.isInCall', 
    'projectedBalances.stockBuyingPower'] """

    # Columns: [0]
    def balances(self) -> pd.DataFrame:
        endpoint = r'https://api.tdameritrade.com/v1/accounts/{}'.format(self.accountID)
        content = get_content(url=endpoint, headers=self.token)
        response = content.json()['securitiesAccount']
        df = pd.json_normalize(response).T
        return df

    # Account positions for a specific account.
    # Index: Symbol
    # Columns:
    """['longQuantity', 'shortQuantity', 'settledLongQuantity', 'settledShortQuantity', 'averagePrice', 
    'marketValue', 'currentDayProfitLoss', 'currentDayProfitLossPercentage', 'maintenanceRequirement', 
    'currentDayCost', 'previousSessionLongQuantity', 'previousSessionShortQuantity', 'instrument.assetType', 
    'instrument.cusip', 'instrument.description', 'instrument.putCall', 'instrument.underlyingSymbol'] """

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
    # Index: TransactionID
    # Columns
    """['type', 'subAccount', 'settlementDate', 'netAmount', 'transactionDate', 'transactionSubType', 
    'cashBalanceEffectFlag', 'description', 'fees.rFee', 'fees.additionalFee', 'fees.cdscFee', 'fees.regFee', 
    'fees.otherCharges', 'fees.commission', 'fees.optRegFee', 'fees.secFee', 'transactionItem.accountId', 
    'transactionItem.cost', 'transactionItem.instrument.symbol', 'transactionItem.instrument.cusip', 
    'transactionItem.instrument.assetType', 'transactionItem.amount', 'transactionItem.price', 
    'transactionItem.instruction', 'orderId', 'orderDate', 'transactionItem.positionEffect', 
    'transactionItem.instrument.underlyingSymbol', 'transactionItem.instrument.optionExpirationDate', 
    'transactionItem.instrument.putCall', 'transactionItem.instrument.description', 'clearingReferenceNumber', 
    'achStatus', 'transactionItem.instrument.type'] """

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
    # Response:
    """[{'session': 'NORMAL', 'duration': 'DAY', 'orderType': 'LIMIT', 'complexOrderStrategyType': 'NONE', 
    'quantity': 1.0, 'filledQuantity': 0.0, 'remainingQuantity': 1.0, 'requestedDestination': 'AUTO', 
    'destinationLinkName': 'AutoRoute', 'price': 460.0, 'orderLegCollection': [{'orderLegType': 'EQUITY', 'legId': 1, 
    'instrument': {'assetType': 'EQUITY', 'cusip': '78462F103', 'symbol': 'SPY'}, 'instruction': 'BUY', 
    'positionEffect': 'OPENING', 'quantity': 1.0}], 'orderStrategyType': 'SINGLE', 'orderId': 5073660086, 
    'cancelable': True, 'editable': True, 'status': 'QUEUED', 'enteredTime': '2021-11-18T23:56:03+0000', 'accountId': 
    455193618}] """

    """[{'session': 'NORMAL', 'duration': 'DAY', 'orderType': 'LIMIT', 'complexOrderStrategyType': 'NONE', 
    'quantity': 1.0, 'filledQuantity': 0.0, 'remainingQuantity': 0.0, 'requestedDestination': 'AUTO', 
    'destinationLinkName': 'AutoRoute', 'price': 460.0, 'orderLegCollection': [{'orderLegType': 'EQUITY', 'legId': 1, 
    'instrument': {'assetType': 'EQUITY', 'cusip': '78462F103', 'symbol': 'SPY'}, 'instruction': 'BUY', 
    'positionEffect': 'OPENING', 'quantity': 1.0}], 'orderStrategyType': 'SINGLE', 'orderId': 5073660086, 
    'cancelable': False, 'editable': False, 'status': 'CANCELED', 'enteredTime': '2021-11-18T23:56:03+0000', 
    'closeTime': '2021-11-18T23:58:59+0000', 'accountId': 455193618}] """

    def orders(self):
        endpoint = r'https://api.tdameritrade.com/v1/accounts/{}'.format(self.accountID)
        params = {'fields': 'orders'}
        content = get_content(url=endpoint, params=params, headers=self.token)
        response = content.json()['securitiesAccount']['orderStrategies']
        # TODO: Fix when no orders
        df = pd.json_normalize(response)
        # TODO: Fix df indexing
        return response
