"""
validate_sync.py

Randomly samples and compares mapped signals from a higher timeframe (e.g., 2h) to a lower timeframe (e.g., 1m)
to verify signal synchronization and mapping quality.
"""

import pandas as pd
import numpy as np
import random

def validate_mapping(df_signal, df_exec, sample_size=10):
    """
    Validates mapping from higher to lower timeframe by sampling and comparing signal integrity.

    Parameters:
    - df_signal: DataFrame containing original signal data (includes 'Close_time', 'Position', 'Rolling_TR', 'Close')
    - df_exec: DataFrame with signals mapped (includes 'Close_time', 'Position', 'Signal_Close', 'Rolling_TR')
    - sample_size: Number of random samples to compare

    Prints mismatches and sample comparisons.
    """

    df_signal['Close_time'] = pd.to_datetime(df_signal['Close_time'])
    df_exec['Close_time'] = pd.to_datetime(df_exec['Close_time'])

    start_time = df_exec['Close_time'].min()
    end_time = df_exec['Close_time'].max()

    signal_rows = df_signal[
        (df_signal['Position'] != 0) &
        (df_signal['Close_time'] >= start_time) &
        (df_signal['Close_time'] <= end_time)
    ]

    print(f"🧾 Usable signals found: {len(signal_rows)}")

    sample_indices = random.sample(list(signal_rows.index), min(sample_size, len(signal_rows)))

    for idx in sample_indices:
        row_signal = df_signal.loc[idx]
        signal_time = row_signal['Close_time']
        match_idx = df_exec['Close_time'].searchsorted(signal_time, side='right')

        if match_idx >= len(df_exec):
            print(f"⚠️ Signal at {signal_time} has no matching lower-TF bar.")
            continue

        row_exec = df_exec.iloc[match_idx]

        print("\n--- Signal Match ---")
        print(f"Signal Time     : {row_signal['Close_time']} → Exec Time: {row_exec['Close_time']}")
        print(f"Signal Position : {row_signal['Position']}     | Exec Position: {row_exec['Position']}")
        print(f"Signal Close    : {row_signal['Close']}        | Exec Signal_Close: {row_exec['Signal_Close']}")
        print(f"Signal TR       : {row_signal['Rolling_TR']}   | Exec TR: {row_exec['Rolling_TR']}")

        # Optional strict checks
        # assert row_signal['Position'] == row_exec['Position'], "Position mismatch!"
        # assert np.isclose(row_signal['Close'], row_exec['Signal_Close'], atol=1e-6), "Close mismatch!"
        # assert np.isclose(row_signal['Rolling_TR'], row_exec['Rolling_TR'], atol=1e-6), "TR mismatch!"

if __name__ == "__main__":
    df_signal = pd.read_csv("data_signal.csv")               # Higher timeframe
    df_exec = pd.read_csv("data_exec_with_signals.csv")      # Lower timeframe with mapped signals

    validate_mapping(df_signal, df_exec)
