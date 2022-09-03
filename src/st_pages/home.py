# Streamlit Homepage

import streamlit as st
from lib import tda
from src.st_pages import screener


# Main Streamlit Homepage
def home():
    st.header("Home")

    ticker = st.text_input(label="Enter Equity Symbol",
                           max_chars=8,
                           placeholder="AAPL",
                           value="AAPL").upper()

    screener.screener(ticker)
