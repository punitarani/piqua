# Streamlit Short Put Screener Page
import streamlit as st

from src.options.short_put_screener import ShortPut


# Short Put Screener Page
def section_shortPutScreener(ticker):
    st.header("Short Put Screener")

    with st.expander('Settings'):
        left_col, middle_col, right_col = st.columns(3)
        with left_col:
            delta_min = st.number_input("Minimum Delta", value=10)
            delta_max = st.number_input("Maximum Delta", value=30)

        with middle_col:
            filter_mode = st.radio(label="Results Details",
                                   options=("Basic", "Advanced", "All"))

    @st.cache(ttl=120, show_spinner=False)
    def shortput_object(t):
        obj = ShortPut(ticker=t)
        return obj

    @st.cache(ttl=120, show_spinner=False)
    def csp_scan(sp_obj, dmin, dmax):
        df = sp_obj.delta_screen(delta_min=dmin, delta_max=dmax, include_stats=True)
        return df

    # Run Screen
    sp = shortput_object(t=ticker)
    results = csp_scan(sp_obj=sp, dmin=delta_min, dmax=delta_max)

    # Filter results output df
    if filter_mode == "Advanced":
        results = results[['symbol', 'description', 'mark', 'bid', 'ask', 'last', 'markChange', 'markPercentChange',
                           'totalVolume', 'openInterest', 'delta', 'theta', 'highPrice', 'lowPrice', 'volatility',
                           'BPE', 'ROC']]
    elif filter_mode == "Basic":
        results = results[['symbol', 'description', 'mark', 'bid', 'delta', 'theta',
                           'openInterest', 'BPE', 'ROC']]

    # Display df
    st.dataframe(results)
