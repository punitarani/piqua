from lib.tda import OptionChain


class ShortPut:
    def __init__(self, ticker):
        self.ticker = ticker
        self.OptionChain_object = OptionChain(ticker=ticker)
        self.oc = self.OptionChain_object.chain_best(dte=45, exclude_weekly=True)
        self.underlying = self.OptionChain_object.underlyingData
        self.underlyingPrice = float(self.underlying.get("mark"))

    def delta_screen(self, delta_max: float = 30, delta_min: float = 10, include_stats: bool = False,
                     minimum_credit: float = 0.5, maximum_credit: float = 2.5, open_interest: int = 25):
        df = self.oc

        # Filter to expiration and puts only
        expiration = df.index.to_list()[0][0]
        df = df.loc[(expiration, 'PUT')]

        # Filter Open Interest
        df = df[df['openInterest'].notna()]
        df = df[df['openInterest'] >= open_interest]

        # Filter minimum credit
        df = df[df['mark'].notna()]
        df = df[df['mark'].between(minimum_credit, maximum_credit)]

        # Filter Delta
        df = df[df['delta'].notna()]
        df = df[df['delta'].between(-delta_max / 100, -delta_min / 100)]

        # Strikes
        strikes = df.index.to_list()

        # Stats
        if include_stats and strikes != []:
            df.reset_index(inplace=True)
            # Get buying power to sell option
            df['BPE'] = df.apply(
                lambda row: max([round(20 * self.underlyingPrice + (float(row.strikePrice) - self.underlyingPrice)
                                       + float(row.mark) * 100, 2),
                                 round(10 * float(row.strikePrice) + float(row.mark) * 100, 2),
                                 round(float(row.mark) * 100 + 50, 2)]), axis=1)

            # Calculate ROC
            df['ROC'] = df.apply(lambda row: round(row.mark * 100 / row.BPE * 100, 2), axis=1)

        return df


if __name__ == "__main__":
    print(ShortPut(ticker='AAPL').delta_screen(include_stats=True))


