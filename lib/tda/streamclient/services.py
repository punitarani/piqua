# Services Fields

from enum import Enum


class Fields:
    account_activity = {
        "0": "subscription_key",
        "1": "account_id",
        "2": "msg_type",
        "3": "msg",
    }

    level_one_fields = {
        "0": "subscription_key",
        "1": "account_id",
        "2": "msg_type",
        "3": "msg",
        "4": "symbol",
        "5": "security_type",
    }

    level_one_equity = {
        "0": "Symbol",
        "1": "Bid Price",
        "2": "Ask Price",
        "3": "Last Price",
        "4": "Bid Size",
        "5": "Ask Size",
        "6": "Ask ID",
        "7": "Bid ID",
        "8": "Total Volume",
        "9": "Last Size",
        "10": "Trade Time",
        "11": "Quote Time",
        "12": "High Price",
        "13": "Low Price",
        "14": "Bid Tick",
        "15": "Close Price",
        "16": "Exchange ID",
        "17": "Marginable",
        "18": "Shortable",
        "19": "Island Bid",
        "20": "Island Ask",
        "21": "Island Volume",
        "22": "Quote Day",
        "23": "Trade Day",
        "24": "Volatility",
        "25": "Description",
        "26": "Last ID",
        "27": "Digits",
        "28": "Open Price",
        "29": "Net Change",
        "30": "52 Week High",
        "31": "52 Week Low",
        "32": "PE Ratio",
        "33": "Dividend Amount",
        "34": "Dividend Yield",
        "35": "Island Bid Size",
        "36": "Island Ask Size",
        "37": "NAV",
        "38": "Fund Price",
        "39": "Exchange Name",
        "40": "Dividend Date",
        "41": "Regular Market Quote",
        "42": "Regular Market Trade",
        "43": "Regular Market Last Price",
        "44": "Regular Market Last Size",
        "45": "Regular Market Trade Time",
        "46": "Regular Market Trade Day",
        "47": "Regular Market Net Change",
        "48": "Security Status",
        "49": "Mark",
        "50": "Quote Time",
        "51": "Trade Time",
        "52": "Regular Market Trade Time",
    }

    level_one_options = {
        "0": "Symbol",
        "1": "Description",
        "2": "Bid Price",
        "3": "Ask Price",
        "4": "Last Price",
        "5": "High Price",
        "6": "Low Price",
        "7": "Close Price",
        "8": "Total Volume",
        "9": "Open Interest",
        "10": "Volatility",
        "11": "Quote Time",
        "12": "Trade Time",
        "13": "Money Intrinsic Value",
        "14": "Quote Day",
        "15": "Trade Day",
        "16": "Expiration Year",
        "17": "Multiplier",
        "18": "Digits",
        "19": "Open Price",
        "20": "Bid Size",
        "21": "Ask Size",
        "22": "Last Size",
        "23": "Net Change",
        "24": "Strike Price",
        "25": "Contract Type",
        "26": "Underlying",
        "27": "Expiration Month",
        "28": "Deliverables",
        "29": "Time Value",
        "30": "Expiration Day",
        "31": "Days to Expiration",
        "32": "Delta",
        "33": "Gamma",
        "34": "Theta",
        "35": "Vega",
        "36": "Rho",
        "37": "Security Status",
        "38": "Theoretical Option Value",
        "39": "Underlying Price",
        "40": "UV Expiration Type",
        "41": "Mark"
    }

    level_one_futures = {
        "0": "Symbol",
        "1": "Bid Price",
        "2": "Ask Price",
        "3": "Last Price",
        "4": "Bid Size",
        "5": "Ask Size",
        "6": "Ask ID",
        "7": "Bid ID",
        "8": "Total Volume",
        "9": "Last Size",
        "10": "Quote Time",
        "11": "Trade Time",
        "12": "High Price",
        "13": "Low Price",
        "14": "Close Price",
        "15": "Exchange ID",
        "16": "Description",
        "17": "Last ID",
        "18": "Open Price",
        "19": "Net Change",
        "20": "Future Percent Change",
        "21": "Exchange Name",
        "22": "Security Status",
        "23": "Open Interest",
        "24": "Mark",
        "25": "Tick",
        "26": "Tick Amount",
        "27": "Product",
        "28": "Future Price Format",
        "29": "Future Trading Hours",
        "30": "Future is Tradable",
        "31": "Future Multiplier",
        "32": "Future is Active",
        "33": "Future Settlement Price",
        "34": "Future Active Symbol",
        "35": "Future Expiration Date"
    }

    book = {
        "0": "Mark",
        "1": "Time",
        "2": "Bids",
        "3": "Asks",
    }

    book_bids = {
        "0": "Price",
        "1": "Volume",
        "2": "Num Bids",
        "3": "Exchange Details"
    }

    book_asks = {
        "0": "Price",
        "1": "Volume",
        "2": "Num Asks",
        "3": "Exchanges"
    }

    book_exchange = {
        "0": "Exchange",
        "1": "Volume",
        "2": "Sequence"
    }

    timesale = {
        "0": "Symbol",
        "1": "Trade Time",
        "2": "Last Price",
        "3": "Last Size",
        "4": "Last Sequence"
    }

    news_headline = {
        "0": "Symbol",
        "1": "Error Code",
        "2": "Story Datetime",
        "3": "Headline ID",
        "4": "Status",
        "5": "Headline",
        "6": "Story ID",
        "7": "Count for Keyword",
        "8": "Keyword Array",
        "9": "Is Hot",
        "10": "Story Source"
    }


class QOS(Enum):
    """
    Quality of service levels
    """

    #: 500ms between updates. Fastest available
    EXPRESS = '0'

    #: 750ms between updates
    REAL_TIME = '1'

    #: 1000ms between updates. Default value.
    FAST = '2'

    #: 1500ms between updates
    MODERATE = '3'

    #: 3000ms between updates
    SLOW = '4'

    #: 5000ms between updates
    DELAYED = '5'


# fields = {
#     "0": "",
#     "1": "",
#     "2": "",
#     "3": "",
#     "4": "",
#     "5": "",
#     "6": "",
#     "7": "",
#     "8": "",
#     "9": "",
#     "10": "",
#     "11": "",
#     "12": "",
#     "13": "",
#     "14": "",
#     "15": "",
#     "16": "",
#     "17": "",
#     "18": "",
#     "19": "",
#     "20": "",
#     "21": "",
#     "22": "",
#     "23": "",
#     "24": "",
#     "25": "",
#     "26": "",
#     "27": "",
#     "28": "",
#     "29": "",
#     "30": "",
#     "31": "",
#     "32": "",
#     "33": "",
#     "34": "",
#     "35": "",
#     "36": "",
#     "37": "",
#     "38": "",
#     "39": "",
#     "40": "",
#     "41": "",
#     "42": "",
#     "43": "",
#     "44": "",
#     "45": "",
#     "46": "",
#     "47": "",
#     "48": "",
#     "49": "",
#     "50": "",
#     "51": "",
#     "52": "",
#     "53": "",
#     "54": "",
#     "55": "",
# }
