# Equity Tests

import unittest

from lib.tda.equity.equity import Equity
from lib.tda.equity.price_history import PriceHistory
from lib.tda.equity.stats import Stats


class EquityTest(unittest.TestCase):
    def test_quote(self):
        ticker = 'SPY'
        data = Equity('SPY').quote()
        self.assertEqual(len(data), 49)
        self.assertEqual(data.columns.tolist(), [ticker])

    def test_quotes(self):
        tickers = ['SPY', 'QQQ', 'IWM']
        data = Equity(tickers).quotes()
        self.assertEqual(data.shape, (49, 3))
        self.assertEqual(data.columns.tolist(), tickers)

    def test_fundamentals(self):
        tickers = ['SPY', 'QQQ', 'IWM']
        data = Equity(tickers).quotes()
        self.assertEqual(data.shape, (49, 3))
        self.assertEqual(data.columns.tolist(), tickers)


class EquityPriceHistoryTest(unittest.TestCase):
    def test_price_history(self):
        data = PriceHistory(ticker='SPY').price_history(period=10, period_type='year',
                                                        frequency_type='daily', frequency=1)
        self.assertEqual(data.columns.tolist(), ['open', 'high', 'low', 'close', 'volume'])
        self.assertAlmostEqual(len(data), 2500, places=-2)

    def test_daily(self):
        data = PriceHistory(ticker='SPY').daily(period=10)
        self.assertEqual(data.columns.tolist(), ['open', 'high', 'low', 'close', 'volume'])
        self.assertAlmostEqual(len(data), 2500, places=-2)

    def test_minute(self):
        data = PriceHistory(ticker='SPY').minute(period=10)
        self.assertEqual(data.columns.tolist(), ['open', 'high', 'low', 'close', 'volume'])
        self.assertAlmostEqual(len(data), 3900, delta=250)


class EquityStatsTest(unittest.TestCase):
    def test_beta(self):
        data = Stats('SPY').beta(period=1, index='SPY')
        self.assertEqual(data, 1)

    def test_correlation(self):
        data = Stats('SPY').correlation(period=1, index='SPY')
        self.assertEqual(data, 1)


# Run All Tests
if __name__ == '__main__':
    unittest.main()
