"""
validate_sync.py

Randomly samples and compares mapped signals from 2h to 1m bars for quality control.
"""

import pandas as pd
import numpy as np
import random

def validate_mapping(df_2h, df_1m, sample_size=10):
    df_1m['Close_time'] = pd.to_datetime(df_1m['Close_time'])
    df_2h['Close_time'] = pd.to_datetime(df_2h['Close_time'])

    start_time = df_1m['Close_time'].min()
    end_time = df_1m['Close_time'].max()

    signal_rows = df_2h[
        (df_2h['Position'] != 0) &
        (df_2h['Close_time'] >= start_time) &
        (df_2h['Close_time'] <= end_time)
    ]

    print(f"🧾 Usable signals found: {len(signal_rows)}")

    sample_indices = random.sample(list(signal_rows.index), min(sample_size, len(signal_rows)))

    for idx in sample_indices:
        row_2h = df_2h.loc[idx]
        signal_time = row_2h['Close_time']
        match_idx = df_1m['Close_time'].searchsorted(signal_time, side='right')

        if match_idx >= len(df_1m):
            print(f"⚠️ Signal at {signal_time} has no match in 1m bars.")
            continue

        row_1m = df_1m.iloc[match_idx]
        print("\n--- Signal Match ---")
        print(f"2h Time: {row_2h['Close_time']} | 1m Time: {row_1m['Close_time']}")
        print(f"2h Pos: {row_2h['Position']} | 1m Pos: {row_1m['Position']}")
        print(f"2h Close: {row_2h['Close']} | 1m Signal_Close: {row_1m['Signal_Close']}")
        print(f"2h TR: {row_2h['Rolling_TR']} | 1m TR: {row_1m['Rolling_TR']}")

        # Optional assertions
        # assert row_2h['Position'] == row_1m['Position'], "Mismatch in Position"
        # assert np.isclose(row_2h['Close'], row_1m['Signal_Close'], atol=1e-6), "Mismatch in Close"
        # assert np.isclose(row_2h['Rolling_TR'], row_1m['Rolling_TR'], atol=1e-6), "Mismatch in TR"

if __name__ == "__main__":
    df_2h = pd.read_csv("data_2h.csv")
    df_1m = pd.read_csv("data_1m_with_signals.csv")
    validate_mapping(df_2h, df_1m)
