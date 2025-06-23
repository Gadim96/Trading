"""
sync_dfs.py

Synchronizes higher-timeframe signals (e.g., 2h) to lower-timeframe execution bars (e.g., 1m).
Useful for aligning model signals with granular execution data for realistic backtesting.
"""

import pandas as pd
import numpy as np

def attach_signals_to_lower_tf(df_signal, df_exec):
    """
    Attaches signal information from a higher-timeframe DataFrame to a lower-timeframe execution DataFrame.

    Parameters:
    - df_signal: DataFrame containing signals (must include 'Close_time', 'Position', 'Rolling_TR', 'Close')
    - df_exec: DataFrame with lower-timeframe execution bars (must include 'Close_time')

    Returns:
    - df_exec: Modified DataFrame with new columns ['Position', 'Rolling_TR', 'Signal_Close']
    """

    df_signal['Close_time'] = pd.to_datetime(df_signal['Close_time'])
    df_exec['Close_time'] = pd.to_datetime(df_exec['Close_time'])

    df_signal = df_signal.sort_values('Close_time').reset_index(drop=True)
    df_exec = df_exec.sort_values('Close_time').reset_index(drop=True)

    # Initialize or overwrite the following columns in execution DataFrame
    df_exec['Position'] = 0
    df_exec['Rolling_TR'] = np.nan
    df_exec['Signal_Close'] = np.nan

    # Only use valid signals (Position ≠ 0)
    signal_rows = df_signal[df_signal['Position'] != 0]
    start_time = df_exec['Close_time'].min()
    end_time = df_exec['Close_time'].max()

    for _, row in signal_rows.iterrows():
        signal_time = row['Close_time']
        if not (start_time <= signal_time <= end_time):
            continue

        match_idx = df_exec['Close_time'].searchsorted(signal_time, side='right')
        if match_idx < len(df_exec):
            df_exec.at[match_idx, 'Position'] = row['Position']
            df_exec.at[match_idx, 'Rolling_TR'] = row['Rolling_TR']
            df_exec.at[match_idx, 'Signal_Close'] = row['Close']

    return df_exec


if __name__ == "__main__":
    # Load your higher and lower timeframe data
    df_signal = pd.read_csv("data_signal.csv")   # e.g., 2h data
    df_exec = pd.read_csv("data_exec.csv")       # e.g., 1m data

    # Perform mapping
    df_exec_synced = attach_signals_to_lower_tf(df_signal, df_exec)

    # Save result
    df_exec_synced.to_csv("data_exec_with_signals.csv", index=False)
    print("✅ Signal mapping complete. Saved to 'data_exec_with_signals.csv'.")
