# Stock Random Walk Predictions

import numpy as np
import scipy
from scipy import sparse
from scipy.sparse.linalg import spsolve
import matplotlib.pyplot as plt
from lib.tda import Equity, PriceHistory


class RandomWalk:
    def __init__(self, ticker: str, days=252, sims=100, step_size=1, r=0.02):
        self.ticker = ticker.upper()
        self.data = Equity(ticker=ticker).quote()
        self.daily = PriceHistory(ticker=ticker).daily(period=1)
        self.daily["returns"] = self.daily["close"].pct_change()

        self.S = self.data.loc["mark", self.ticker]
        self.V = self.daily["returns"].std() * np.sqrt(252)

        self.days = days
        self.sims = sims
        self.stepSize = step_size
        self.r = r

    def walk(self):
        # Convert annualized rate to a daily value
        r = self.r / 252.0

        # Get
        sigma = self.V / np.sqrt(252.0)

        # Get a normally distributed array of values
        normal = np.random.normal(size=(self.sims * self.days + self.sims - 1))

        # Calculate daily percent change in stock price based
        dS_dt = r * self.stepSize + sigma * normal

        ones = -np.ones((self.sims * self.days + self.sims))

        ones[0:-1:self.days + 1] = 1

        dS_dt[self.days:self.days * self.sims + self.sims:self.days + 1] = -1
        d = [dS_dt + 1, ones]
        K = [-1, 0]

        M = scipy.sparse.diags(d, K, format='csc')

        p = np.zeros((self.sims * self.days + self.sims, 1))
        p[0:-1:self.days + 1] = self.S

        s = scipy.sparse.linalg.spsolve(M, p)

        s = np.reshape(s, (self.sims, self.days + 1))

        return s

    def plot(self):
        data = self.walk()
        plt.plot(data.transpose())

        return data


if __name__ == "__main__":
    walk = RandomWalk(ticker="AAPL").plot()
