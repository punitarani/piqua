
import streamlit as st
from lib import tda

from src.st_pages.home import home
from src.st_pages.portfolio import portfolio
from src.st_pages.stocks import stocks
from src.st_pages.options import options


# Page config
st.set_page_config(page_title="Piqua", layout="wide")
st.title("Piqua")


# Check if TD API Auth
@st.cache
def check_td_auth() -> dict:
    auth_token = tda.get_token(test=True)
    return auth_token


# Call function
check_td_auth()


# Navigation
pages = ["Home", "Portfolio", "Stocks", "Options"]
page = st.selectbox(label="Navigation", options=pages, key="Navigation")

# Navigation page matching
match page:
    case "Home":
        home()
    case "Portfolio":
        portfolio()
    case "Stocks":
        stocks()
    case "Options":
        options()
