# feature_engineering.py

"""
Feature Engineering Script
---------------------------
Generates return, volatility, momentum, and volume-based features
for financial time series modeling.

Includes optional GARCH(1,1) volatility prediction logic.
"""

import numpy as np
import pandas as pd
from arch import arch_model
from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt

# ------------------ #
# Basic Feature Engineering
# ------------------ #
def add_basic_features(df):
    df['Return_1'] = df['Close'].pct_change(1)
    df['Return_2'] = df['Close'].pct_change(2)
    df['Return_3'] = df['Close'].pct_change(3)
    df['Log_Return'] = np.log(df['Close']).diff()
    df['Vol_6'] = df['Log_Return'].rolling(6).std()
    df['Vol_20'] = df['Log_Return'].rolling(20).std()
    df['Vol_50'] = df['Log_Return'].rolling(50).std()
    df['Vol_Ratio'] = df['Vol_6'] / (df['Vol_20'] + 1e-9)
    df['Vol_6_Z'] = (df['Vol_6'] - df['Vol_6'].rolling(20).mean()) / (df['Vol_6'].rolling(20).std() + 1e-9)
    df['Momentum_3'] = df['Close'] - df['Close'].shift(3)
    df['Momentum_10'] = df['Close'] - df['Close'].shift(10)
    df['MA_slope_10'] = df['Close'].rolling(10).mean().diff()
    df['Price_MA_20_ratio'] = df['Close'] / (df['Close'].rolling(20).mean() + 1e-9)
    df['SignedVol'] = df['Return_1'] * df['Vol_6']
    df['SignedVol_EMA10'] = df['SignedVol'].ewm(span=10).mean()
    df['ZVolume'] = (df['Volume'] - df['Volume'].rolling(20).mean()) / (df['Volume'].rolling(20).std() + 1e-9)
    return df

# ------------------ #
# GARCH Volatility Forecasting
# ------------------ #
#The GARCH model does one step predictions using a rolling window
def compute_garch_forecast(df, log_return_col='Log_Return', window=1000):
    df['GARCH_Prediction'] = np.nan
    df['Forecast_Vol'] = np.nan
    garch_input = df[log_return_col] * 100

    for i in range(window, len(df) - 1):
        train_data = garch_input.iloc[i - window:i].dropna()
        if len(train_data) < window:
            continue

        garch_model = arch_model(train_data, vol='GARCH', p=1, q=1, mean='Constant', dist='t')
        garch_fit = garch_model.fit(disp='off')
        forecast = garch_fit.forecast(horizon=1)
        variance = forecast.variance.values[-1, 0]
        vol = np.sqrt(variance)

        df.loc[df.index[i + 1], 'GARCH_Prediction'] = variance
        df.loc[df.index[i + 1], 'Forecast_Vol'] = vol

    df['GARCH_vol_1'] = np.sqrt(df['GARCH_Prediction'])
    q_low, q_high = df['GARCH_vol_1'].quantile([0.01, 0.99])
    df['GARCH_vol_1_clipped'] = df['GARCH_vol_1'].clip(q_low, q_high)
    df['GARCH_vs_Realized'] = df['GARCH_vol_1_clipped'] / (df['Vol_6'] + 1e-6)
    df['GARCH_vs_Realized'] = df['GARCH_vs_Realized'].clip(0, 5)
    df['GARCH_Z'] = (
        (df['GARCH_vol_1_clipped'] - df['GARCH_vol_1_clipped'].rolling(50).mean()) /
        df['GARCH_vol_1_clipped'].rolling(50).std()
    ).clip(-5, 5)
    return df


# ------------------ #
# Final Feature List Used in Model
# ------------------ #
feature_cols = [
    'Return_1', 'Return_2', 'Return_3',
    'Log_Return',
    'Vol_6', 'Vol_20', 'Vol_50', 'Vol_Ratio', 'Vol_6_Z',
    'Momentum_3', 'Momentum_10', 'MA_slope_10', 'Price_MA_20_ratio',
    'SignedVol', 'SignedVol_EMA10',
    'ZVolume', 'GARCH_vol_1_clipped', 'GARCH_vs_Realized', 'GARCH_Z',
    # Add engineered RSI and MACD here if applicable
]

# Usage (Jupyter/Script)
# df = add_basic_features(df)
# df = compute_garch_forecast(df)
# df.dropna(subset=feature_cols).reset_index(drop=True)

#The block below is to evaluate GARCH predicttions, it also produces a plot
# --- Convert GARCH variance to volatility ---
df['Forecast_Vol'] = np.sqrt(df['GARCH_Prediction'])

# --- Realized Volatility: 5-period rolling std of FracDiff_Close ---
df['Realized_Vol'] = (df['Log_Return']*100).rolling(window=5).std()

# --- Drop rows with missing values ---
df.dropna(subset=['Forecast_Vol', 'Realized_Vol'], inplace=True)

# --- Compute RMSE ---
rmse = np.sqrt(mean_squared_error(df['Realized_Vol'], df['Forecast_Vol']))
print(f"RMSE of GARCH volatility forecast: {rmse:.6f}")

# --- Plot Forecast vs. Realized Volatility ---
plt.figure(figsize=(12,6))
plt.plot(df.index, df['Realized_Vol'], label='Realized Volatility (5-period STD)', alpha=0.9)
plt.plot(df.index, df['Forecast_Vol'], label='GARCH Forecasted Volatility', alpha=0.8)
plt.xlabel('Time')
plt.ylabel('Volatility')
plt.title('GARCH Forecast vs. Realized Volatility')
plt.legend()
plt.tight_layout()
plt.show()

