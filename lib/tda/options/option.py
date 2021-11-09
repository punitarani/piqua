# TD Ameritrade API Option data

import pandas as pd

from ..auth import get_token, get_content


# Options Data
class Option:
    def __init__(self, ticker: str = None, tickers: list = None, option_symbol: str or list = None):
        self.token = get_token()
        self.ticker = ticker
        self.tickers = tickers if tickers is not None else [ticker]

        if isinstance(option_symbol, str):
            self.symbol = option_symbol
        elif isinstance(option_symbol, list):
            self.symbol = option_symbol[0]
            self.symbols = option_symbol

    # GET quote for a symbol
    def quote(self):
        endpoint = r'https://api.tdameritrade.com/v1/marketdata/{}/quotes'.format(self.symbol)
        content = get_content(url=endpoint, headers=self.token)
        response = content.json()
        df = pd.DataFrame.from_dict(response)
        return df

    # GET quote for one or more symbols
    def quotes(self):
        endpoint = r'https://api.tdameritrade.com/v1/marketdata/quotes'
        params = {'symbol': ','.join(self.symbols)}
        content = get_content(url=endpoint, params=params, headers=self.token)
        response = content.json()
        df = pd.DataFrame.from_dict(response).T
        return df

    # Estimates the buying power effect
    def bpe(self, short=False, quote=None, override_method=None):
        if quote is not None:
            quote = quote
        else:
            quote = self.quote()
        mark = quote.loc['mark', self.symbol]
        cost = mark * 100

        # Calculate BPE
        if not short:
            return round(float(cost), 2)
        else:
            underlying_price = quote.loc['underlyingPrice', self.symbol]
            strike = quote.loc['strikePrice', self.symbol]
            put_call = quote.loc['contractType', self.symbol]

            # BPE Calculation 1
            otm_amount = (strike - underlying_price) * 100
            bpe1 = 20 * underlying_price + otm_amount + cost

            # BPE Calculation 2
            bpe2 = 10 * underlying_price + cost if put_call == 'C' else 10 * strike + cost

            # BPE Calculation 3
            bpe3 = cost + 50

            if override_method == 1:
                return round(bpe1, 2)
            elif override_method == 2:
                return round(bpe2, 2)
            elif override_method == 3:
                return round(bpe3, 2)
            else:
                bpe = max([bpe1, bpe2, bpe3])
                return round(bpe, 2)

    # GET underlying data
    def underlying(self):
        endpoint = r'https://api.tdameritrade.com/v1/marketdata/chains'
        params = {'symbol': self.ticker}
        content = get_content(url=endpoint, params=params, headers=self.token)
        response = content.json()

        data = {k: response[k] for k in ['symbol', 'underlyingPrice', 'interestRate', 'volatility']}
        df = pd.json_normalize(data).set_index('symbol', inplace=False).T
        return df
