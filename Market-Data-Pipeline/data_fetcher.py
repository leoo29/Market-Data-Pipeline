# -*- coding: utf-8 -*-
import yfinance as yf
import pandas as pd
import sys


def fetch_data(ticker, start, end):
    try:
        df = yf.download(ticker, start=start, end=end, progress=False, auto_adjust=True)
    except Exception as e:
        print("NETWORK ERROR for '{}': {}".format(ticker, e))
        sys.exit(1)

    # yfinance returns an empty DataFrame for invalid tickers — catch it explicitly
    if df is None or df.empty:
        print("ERROR: No data found for '{}'.".format(ticker))
        print("  -> Check the symbol at https://finance.yahoo.com")
        print("  -> Valid examples: AAPL, MC.PA, BTC-USD, ^FCHI, SPY")
        sys.exit(1)

    # Flatten multi-index columns (recent yfinance behavior)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    cols_needed   = ["Open", "High", "Low", "Close", "Volume"]
    cols_available = [c for c in cols_needed if c in df.columns]
    df = df[cols_available].copy()

    return df
