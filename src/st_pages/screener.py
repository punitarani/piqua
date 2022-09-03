# Screener Page

import streamlit as st

from src.st_pages.subpages import short_put_screener_section as short_put


# Display Short Put Screener Page
def screener(ticker):
    short_put.section_shortPutScreener(ticker=ticker)
