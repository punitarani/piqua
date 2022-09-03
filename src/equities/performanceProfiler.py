# Calculate the profile of a stocks performance

import numpy as np
import pandas as pd

from lib.tda import PriceHistory


class PerformanceProfile:
    def __init__(self, ticker):
        self.Ticker = ticker.upper()

        self.Daily = None
        self.daily(period=20)

    # Get daily dataframe
    def daily(self, period: int = 20) -> pd.DataFrame:
        daily = PriceHistory(self.Ticker).daily(period=period)
        self.Daily = daily
        return daily

    # Get daily performance percentages dataframe
    def dailyPerformance(self, period: int = 10) -> pd.DataFrame:
        # Filter Period
        dailyPerf = self.Daily.copy().tail(period * 252)

        # Calculate daily percentage change and replace NaN values with 0
        dailyPerf["Performance"] = dailyPerf["close"].pct_change().fillna(0)
        return dailyPerf

    # Get  daily performance percentages array
    def performance(self, period: int = 10) -> np.array:

        perf = self.dailyPerformance(period=period)
        return np.array(perf["Performance"].to_list())

    # Calculate volatility over period
    def volatility(self, period: int = 10) -> float:
        perf = self.performance(period=period)

        # Calculate volatility
        vol = perf.std() * np.sqrt(252)
        return vol


if __name__ == "__main__":
    ticker_input = "SPY"
    profiler = PerformanceProfile(ticker=ticker_input)

    print(profiler.daily())
