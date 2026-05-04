# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np


def calculate_metrics(df: pd.DataFrame, risk_free_rate: float = 0.04) -> pd.DataFrame:
    """
    Computes all quantitative metrics on a clean OHLCV DataFrame.

    Args:
        df             : Cleaned DataFrame with at least a 'Close' column
        risk_free_rate : Annual risk-free rate used for Sharpe calculation (default: 4%)

    Returns:
        DataFrame enriched with metric columns
    """
    df = df.copy()

    # Daily return: (P_t - P_{t-1}) / P_{t-1}
    df["Daily_Return"] = df["Close"].pct_change()

    # Cumulative return: rebased to 0 at start, shows total growth
    df["Cumulative_Return"] = (1 + df["Daily_Return"]).cumprod() - 1

    # Rolling 30-day volatility, annualized (x sqrt(252) trading days)
    df["Volatility_30d"] = (
        df["Daily_Return"]
        .rolling(window=30, min_periods=15)
        .std()
        * np.sqrt(252)
    )

    # Rolling all-time high and drawdown from peak
    df["Rolling_Max"] = df["Close"].cummax()
    df["Drawdown"]    = (df["Close"] - df["Rolling_Max"]) / df["Rolling_Max"]

    # Rolling 30-day Sharpe Ratio (annualized)
    # Formula: (annualized_return - risk_free_rate) / annualized_volatility
    rolling_mean  = df["Daily_Return"].rolling(window=30, min_periods=15).mean()
    rolling_std   = df["Daily_Return"].rolling(window=30, min_periods=15).std()
    annual_return = rolling_mean * 252
    annual_vol    = rolling_std  * np.sqrt(252)
    df["Sharpe_30d"] = (annual_return - risk_free_rate) / annual_vol

    return df
