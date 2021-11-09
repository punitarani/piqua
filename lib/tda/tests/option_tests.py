# Option Tests

import unittest
from datetime import datetime
from lib.tda.options.option_chain import get_unix_time, OptionChain


class OptionTest(unittest.TestCase):
    def test_get_unix_time(self):
        dt = datetime.strptime("01/01/2020 00:00:00", "%d/%m/%Y %H:%M:%S")
        unix = get_unix_time(dt)
        self.assertEqual(unix, 1577836800000.0)


class OptionChainTest(unittest.TestCase):
    def test_chain(self):
        ocdf = OptionChain(ticker='SPY').chain()
        columns = ocdf.columns.tolist()
        true_columns = ['symbol', 'description', 'exchangeName', 'bid', 'ask', 'last', 'mark', 'bidSize', 'askSize',
                        'bidAskSize', 'lastSize', 'highPrice', 'lowPrice', 'openPrice', 'closePrice', 'totalVolume',
                        'tradeDate', 'tradeTimeInLong', 'quoteTimeInLong', 'netChange', 'volatility', 'delta', 'gamma',
                        'theta', 'vega', 'rho', 'openInterest', 'timeValue', 'theoreticalOptionValue',
                        'theoreticalVolatility', 'optionDeliverablesList', 'daysToExpiration', 'expirationType',
                        'lastTradingDay', 'multiplier', 'settlementType', 'deliverableNote', 'isIndexOption',
                        'percentChange', 'markChange', 'markPercentChange', 'inTheMoney', 'nonStandard', 'mini']
        self.assertEqual(columns.sort(), true_columns.sort())

    def test_chain_best(self):
        ocdf = OptionChain(ticker='SPY').chain_best()
        columns = ocdf.columns.tolist()
        true_columns = ['symbol', 'description', 'exchangeName', 'bid', 'ask', 'last', 'mark', 'bidSize', 'askSize',
                        'bidAskSize', 'lastSize', 'highPrice', 'lowPrice', 'openPrice', 'closePrice', 'totalVolume',
                        'tradeDate', 'tradeTimeInLong', 'quoteTimeInLong', 'netChange', 'volatility', 'delta', 'gamma',
                        'theta', 'vega', 'rho', 'openInterest', 'timeValue', 'theoreticalOptionValue',
                        'theoreticalVolatility', 'optionDeliverablesList', 'daysToExpiration', 'expirationType',
                        'lastTradingDay', 'multiplier', 'settlementType', 'deliverableNote', 'isIndexOption',
                        'percentChange', 'markChange', 'markPercentChange', 'inTheMoney', 'nonStandard', 'mini']
        self.assertEqual(columns.sort(), true_columns.sort())


# Run All Tests
if __name__ == '__main__':
    unittest.main()
