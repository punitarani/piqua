# Probability of 50% Profit Calculator
import pandas as pd

from lib.tda.options import OptionChain

import numpy as np
import scipy
from scipy.stats import norm


class POP50:
    def __init__(self, ticker: str, exp: str | None):
        self.ticker = ticker.upper()  # Ticker:   AAPL
        self.exp = exp  # Exp:      YYYY-MM-DD

        self.OC = OptionChain(ticker=self.ticker)
        self.chain = self.getOC()
        self.underlying = self.OC.underlyingData.get("mark")

    # Get unfiltered Options Chain for Ticker
    def getOC(self) -> pd.DataFrame:
        ocdf = self.OC.chain(include_quotes=True)
        return ocdf

    # Get specific option from Options Chain
    def getOption(self, strike: float, putcall: str):
        option = self.chain.loc[(self.exp, putcall, strike)]
        return option

    def Single(self, strike: float, putcall: str):
        # Default values
        sims = 1000
        days = 252
        step_size = 1

        option = self.getOption(strike, putcall)

        # Risk free rate: 1%
        r = 0.01 / 252

        # Volatility
        vol = option['volatility'] / 252

        # Create a normally distributed array
        normal = np.random.normal(size=(sims * days + sims - 1))

        # Create a normally distributed change in equity price
        ds = (r * step_size) + (vol * normal)

        ones = -np.ones((sims * days + sims))
        ones[0:-1:days + 1] = 1

        ds[days:days * sims + sims:days + 1] = -1
        d = [ds + 1, ones]
        k = [-1, 0]

        print(normal)
        print(ds)


if __name__ == "__main__":
    print("PoP 50% Calculator")

    # Get user Underlying input
    ticker_input = input("Ticker: ").upper()

    # Create POP50 object
    p50 = POP50(ticker_input, None)

    # Get indices
    indices = p50.chain.index.to_list()

    # Get user input for expiration
    exps = []
    for e in indices:
        if e[0] not in exps:
            exps.append(e[0])
    print("Available Expirations: ")
    for expiration in exps:
        print(expiration)
    expiration_input = input("Expiration: ")
    p50.exp = expiration_input

    # Get user input for put/call
    putcall_input = input("PUT or CALL: ").upper()

    # Get user input for strike
    print("Available Strikes: ")
    strikes = [s[-1] for s in indices if ((s[0] == expiration_input) and (s[1] == putcall_input))]
    for s in strikes:
        print(s)
    strike_input = float(input("Strike: "))

    print(p50.Single(strike=strike_input, putcall=putcall_input))
