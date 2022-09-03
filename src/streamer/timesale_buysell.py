cache = {"ts": None,
         "qt": None}

qt_cache = {}
ts_cache = {}


select_futures_tickers = ["/ES", "/NQ"]


class TimeSaleFutures:
    def __init__(self, msg):

        # Get and update Timesale and quote messages
        if "TIMESALE_FUTURES" in msg.keys():
            self.timesale = msg.get("TIMESALE_FUTURES")

            cache.update({"ts": self.timesale})
            self.quote = cache.get("qt")

        elif "LEVELONE_FUTURES" in msg.keys():
            self.quote = msg.get("LEVELONE_FUTURES")

            cache.update({"qt": self.quote})
            self.timesale = cache.get("ts")

        self.update_cache()

        if "TIMESALE_FUTURES" in msg.keys():
            self.ticker_scan = msg.get("TIMESALE_FUTURES").keys()
            self.main()
        else:
            self.ticker_scan = []

    def __call__(self, *args, **kwargs):
        self.update_cache()
        self.main()

    def update_cache(self):
        ts_keys = ["Last Price", "Last Size", "Trade Time"]
        qt_keys = ["Ask Price", "Bid Price", "Trade Time"]

        # Update Timesale Cache
        if self.timesale is not None:
            timesale_tickers = self.timesale.keys()

            for ticker in timesale_tickers:
                ticker_ts = self.timesale.get(ticker)

                ticker_ts_keys = ticker_ts.keys()

                if ticker not in ts_cache.keys():
                    ts_cache.update({ticker: {}})

                ts_cache_ticker = ts_cache.get(ticker)

                for ts_key in ts_keys:
                    if ts_key in ticker_ts_keys:
                        ts_cache_ticker.update({ts_key: ticker_ts.get(ts_key)})

        # Update Quote Cache
        if self.quote is not None:
            quote_tickers = self.quote.keys()

            for ticker in quote_tickers:
                ticker_qt = self.quote.get(ticker)

                ticker_qt_keys = ticker_qt.keys()

                if ticker not in qt_cache.keys():
                    qt_cache.update({ticker: {}})

                qt_cache_ticker = qt_cache.get(ticker)

                for qt_key in qt_keys:
                    if qt_key in ticker_qt_keys:
                        qt_cache_ticker.update({qt_key: ticker_qt.get(qt_key)})

    def main(self):
        for ticker in self.ticker_scan and ts_cache.keys() and qt_cache.keys():
            qt_cache_ticker = qt_cache.get(ticker)
            ts_cache_ticker = ts_cache.get(ticker)

            bid = qt_cache_ticker.get("Bid Price")
            ask = qt_cache_ticker.get("Ask Price")
            mid = (bid + ask) / 2
            quote_time = qt_cache_ticker.get("Trade Time")

            price = ts_cache_ticker.get("Last Price")
            size = ts_cache_ticker.get("Last Size")
            trade_time = ts_cache_ticker.get("Trade Time")

            buy_sell = "BUY"

            if quote_time <= trade_time + 1:
                if price < mid:
                    buy_sell = "SELL"

            print(f"{ticker}: {buy_sell} {size} for ${price}")

