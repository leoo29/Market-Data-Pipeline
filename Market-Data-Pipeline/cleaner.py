# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np


def clean_data(df):
    initial_len = len(df)

    df = df.dropna(how="all")
    df = df[~df.index.duplicated(keep="first")]
    df = df.sort_index()

    if "Close" in df.columns:
        df = df[df["Close"] > 0]

    if "Volume" in df.columns:
        df = df[df["Volume"] > 0]

    # Remove days with extreme price moves (>80%) — likely data errors
    if "Close" in df.columns:
        daily_change = df["Close"].pct_change().abs()
        extreme_days = daily_change > 0.80
        nb_outliers  = extreme_days.sum()
        if nb_outliers > 0:
            print("  WARNING: {} day(s) with >80% variation removed".format(nb_outliers))
            df = df[~extreme_days]

    # Forward-fill remaining NaNs on price columns
    price_cols = [c for c in ["Open", "High", "Low", "Close"] if c in df.columns]
    df[price_cols] = df[price_cols].ffill()
    df = df.dropna(subset=["Close"])

    removed = initial_len - len(df)
    if removed > 0:
        print("  INFO: {} row(s) removed during cleaning".format(removed))

    return df
