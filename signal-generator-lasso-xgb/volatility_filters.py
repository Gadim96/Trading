"""
volatility_filters.py

Implements a mean-reversion signal generator based on GARCH volatility cooldown
and return direction thresholds.
"""

import numpy as np
import pandas as pd

def generate_vol_cooling_mean_reversion_signals(df, garch_col='GARCH_Prediction', return_col='Log_Return',
                                                return_window=8, vol_lookback=3, return_thresh=None,
                                                vol_ratio_thresh=0.75):
    """
    Generate counter-trend signals when volatility cools down and price overextends.

    Parameters:
    - df: DataFrame with GARCH and return columns
    - garch_col: column with current GARCH forecast
    - return_col: return series (e.g., log returns)
    - return_window: window over which to sum returns
    - vol_lookback: how many bars to average past GARCH
    - return_thresh: optional custom threshold for return quantiles
    - vol_ratio_thresh: max % of past GARCH mean to qualify as "cooled off"

    Returns:
    - df: DataFrame with added 'Position' column
    """
    df = df.copy()
    df['Past_GARCH_Mean'] = df[garch_col].rolling(vol_lookback).mean().shift(1)
    df['Vol_Cooled'] = df[garch_col] < df['Past_GARCH_Mean'] * vol_ratio_thresh
    df['Recent_Return_Sum'] = df[return_col].rolling(return_window).sum()

    if return_thresh is None:
        lower = df['Recent_Return_Sum'].quantile(0.3)
        upper = df['Recent_Return_Sum'].quantile(0.7)
        print(f"Return thresholds (30–70%): {lower:.4f}, {upper:.4f}")
    else:
        lower = -abs(return_thresh)
        upper = abs(return_thresh)

    conditions = [
        (df['Vol_Cooled']) & (df['Recent_Return_Sum'] < lower),
        (df['Vol_Cooled']) & (df['Recent_Return_Sum'] > upper)
    ]
    choices = [1, -1]
    df['Position'] = np.select(conditions, choices, default=0)

    return df
