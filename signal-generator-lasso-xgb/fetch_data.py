from binance.client import Client
import pandas as pd

#as an exaple, user can choose any other crypto symbol, this is for those that would like to usee crypto data
def fetch_binance_data(symbol="ADAUSDT", interval="1m", desired_bars=50000): 
    client = Client()
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
    df = df.astype({"Open": float, "High": float, "Low": float, "Close": float, "Volume": float})
    df["Open_time"] = pd.to_datetime(df["Open_time"], unit='ms')
    df["Close_time"] = pd.to_datetime(df["Close_time"], unit='ms')
    return df.sort_values(by="Open_time").reset_index(drop=True)

#this is in case the user wants to use crypto data from binance
api_key = "your api key"         
api_secret = "api secret key"

#using the function, if testing lower frequency data I suggest also getting 1 minute data, for a more accurate backtest
#I show how and why I did it in another script in this folder

df = fetch_binance_data()
