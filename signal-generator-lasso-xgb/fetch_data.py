"""
data_fetch.py

Fetch historical crypto futures data from Binance.
This function retrieves and structures 1-minute price data into a clean DataFrame.

Author: Gadim Gadimov
"""

import pandas as pd
from binance.client import Client

def fetch_binance_data(symbol="ADAUSDT", interval="1m", desired_bars=50000):
    """
    Fetch historical futures data from Binance.

    Parameters:
        symbol (str): Trading pair (default "ADAUSDT").
        interval (str): Time interval (default "1m").
        desired_bars (int): Number of data points to retrieve (max 1000 per API call).

    Returns:
        pd.DataFrame: Cleaned and sorted OHLCV data.
    """
    client = Client()  # <-- Replace with authenticated client for private access
    all_klines = []
    end_time = None
    fetched = 0

    while fetched < desired_bars:
        limit = min(1000, desired_bars - fetched)
        klines = client.futures_klines(symbol=symbol, interval=interval, limit=limit, endTime=end_time)
        if not klines:
            break
        all_klines.extend(klines)
        fetched += len(klines)
        end_time = klines[0][0] - 1

    df = pd.DataFrame(all_klines, columns=[
        "Open_time", "Open", "High", "Low", "Close", "Volume",
        "Close_time", "Quote_asset_volume", "Number_of_trades",
        "Taker_buy_base_asset_volume", "Taker_buy_quote_asset_volume", "Ignore"
    ])

    df[["Open", "High", "Low", "Close", "Volume"]] = df[["Open", "High", "Low", "Close", "Volume"]].astype(float)
    df["Open_time"] = pd.to_datetime(df["Open_time"], unit='ms')
    df["Close_time"] = pd.to_datetime(df["Close_time"], unit='ms')

    return df.sort_values("Open_time").reset_index(drop=True)

# Example usage:
if __name__ == "__main__":
    # For public GitHub repos, do not include real API keys
    # api_key = "your_api_key"
    # api_secret = "your_api_secret"

    # Example usage without authentication (public endpoints only)
    df = fetch_binance_data()
    print(df.head())
