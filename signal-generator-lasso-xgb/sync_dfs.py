"""
attach_signals.py

Synchronizes 2-hour signals to 1-minute execution bars for granular backtesting.
"""

import pandas as pd
import numpy as np

def attach_signals_to_lower_tf(df_2h, df_1m):
    # Ensure datetime format and sort
    df_1m['Close_time'] = pd.to_datetime(df_1m['Close_time'])
    df_2h['Close_time'] = pd.to_datetime(df_2h['Close_time'])
    df_1m = df_1m.sort_values('Close_time').reset_index(drop=True)
    df_2h = df_2h.sort_values('Close_time').reset_index(drop=True)

    # Initialize new columns in 1m DataFrame
    df_1m['Position'] = 0
    df_1m['Rolling_TR'] = np.nan
    df_1m['Signal_Close'] = np.nan

    # Filter valid signals
    signal_rows = df_2h[df_2h['Position'] != 0]
    start_time = df_1m['Close_time'].min()
    end_time = df_1m['Close_time'].max()

    for _, row in signal_rows.iterrows():
        signal_time = row['Close_time']
        if not (start_time <= signal_time <= end_time):
            continue

        match_idx = df_1m['Close_time'].searchsorted(signal_time, side='right')
        if match_idx < len(df_1m):
            df_1m.at[match_idx, 'Position'] = row['Position']
            df_1m.at[match_idx, 'Rolling_TR'] = row['Rolling_TR']
            df_1m.at[match_idx, 'Signal_Close'] = row['Close']

    return df_1m

if __name__ == "__main__":
    df_2h = pd.read_csv("data_2h.csv")
    df_1m = pd.read_csv("data_1m.csv")

    df_1m_synced = attach_signals_to_lower_tf(df_2h, df_1m)
    df_1m_synced.to_csv("data_1m_with_signals.csv", index=False)
    print("✅ Signal attachment complete. Output saved as 'data_1m_with_signals.csv'.")
