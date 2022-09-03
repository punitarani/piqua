# Build on top of PerformanceProfiler to add custom features

import numpy as np
import pandas as pd

from src.equities.performanceProfiler import PerformanceProfile


class CustomProfile:
    def __init__(self, ticker):
        self.Ticker = ticker.upper()

        self.Profiler = PerformanceProfile(ticker=ticker)

        self.Daily: pd.DataFrame = self.Profiler.daily(period=20).copy()

    @staticmethod
    def calculateVolatility(df: pd.DataFrame) -> float:
        v = df["Performance"].std() * np.sqrt(252)
        return v

    def historicalVolatility(self, period: int = 252):

        vols = []
        daily = self.Daily
        daily["Performance"] = daily["close"].pct_change()
        for i in range(len(self.Daily) - period):
            daily = self.Daily.iloc[i:i+period]
            vols.append(self.calculateVolatility(daily))

        return vols


if __name__ == "__main__":
    ticker_input = "AAPL"
    profiler = CustomProfile(ticker_input)

    vs = profiler.historicalVolatility()

    print(vs)
