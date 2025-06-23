"""
generate_signals.py

Generates 3-class directional signals using XGBoost probabilities and filters
them based on confidence, gap, and volatility regime metrics.
"""

import pandas as pd

def generate_xgb_signals(df, conf_thresh=0.7, gap_thresh=0.2):
    """
    Applies filtering logic to XGBoost output to assign long/short positions.

    Parameters:
    - df: DataFrame with columns ['XGB_Prediction', 'XGB_Long_Conf', 'XGB_Short_Conf', 'Confidence_Gap', 'GARCH_vol_1_clipped', 'Vol_6']
    - conf_thresh: minimum confidence threshold for long/short signals
    - gap_thresh: minimum confidence gap between strongest and second class

    Returns:
    - df: DataFrame with 'Position' column added
    """

    df['Long_Signal'] = (
        (df['XGB_Prediction'] == 2) &
        (df['XGB_Long_Conf'] > conf_thresh) &
        (df['Confidence_Gap'] > gap_thresh)
    )

    df['Short_Signal'] = (
        (df['XGB_Prediction'] == 0) &
        (df['XGB_Short_Conf'] > conf_thresh) &
        (df['Confidence_Gap'] > gap_thresh)
    )

    df['Position'] = 0
    df.loc[df['Long_Signal'], 'Position'] = 1
    df.loc[df['Short_Signal'], 'Position'] = -1

    print(f"✅ XGBoost Signal Stats → Long: {df['Long_Signal'].sum()} | Short: {df['Short_Signal'].sum()} | Flat: {(df['XGB_Prediction'] == 1).sum()}")

    return df
