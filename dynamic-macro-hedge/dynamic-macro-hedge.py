#!/usr/bin/env python3
"""
Dynamic Macro Hedge Model
-------------------------------------------------
• Diversified portfolio: SPY, QQQ, EEM, GLD  (inv-vol weight)
• Measures beta to CPI & clipped 4-day Fed-Funds shocks
• Applies covariance hedge with 10-Year futures (ZN=F) & DXY
• Prints volatility stats, saves five PNG charts

"""

import datetime as dt
from pathlib import Path

import numpy as np
import pandas as pd
import yfinance as yf
import pandas_datareader.data as web
import matplotlib.pyplot as plt
import statsmodels.api as sm


# ------------- plotting & output ---------------------------
plt.style.use("seaborn-v0_8-whitegrid")
FIG_DIR = Path("figures")
FIG_DIR.mkdir(exist_ok=True)

# ------------- 1. DATA -------------------------------------
START = "2015-01-01"
END   = dt.date.today().strftime("%Y-%m-%d")

def fetch_prices(tickers):
    px = yf.download(tickers, start=START, end=END,
                     auto_adjust=True, progress=False)["Close"]
    if isinstance(px.columns, pd.MultiIndex):
        px = px["Close"]
    return px

# 1.1 Portfolio: SPY, QQQ, EEM, GLD  (equal-weight)
tickers_port = ["SPY", "QQQ", "EEM", "GLD"]
ret_port = (
    fetch_prices(tickers_port)
      .pct_change(fill_method=None)
      .dropna()
)
# Risk-weighted (inverse volatility) portfolio
vols = ret_port.rolling(63).std().iloc[-1]
inv_vol_weights = 1 / vols
weights = inv_vol_weights / inv_vol_weights.sum()
portfolio_ret = (ret_port * weights).sum(axis=1).rename("PORT")


# 1.2 Hedge assets: 10-Y futures + DXY
hedge_px = fetch_prices(["ZN=F", "DX-Y.NYB", "VIXY", "LQD", "HYG", "USO", "GLD"])

hedge_ret = (
    hedge_px.pct_change(fill_method=None)
            .dropna()
            .rename(columns={
                "ZN=F": "T10Y",
                "DX-Y.NYB": "DXY",
                "VIXY": "VIXY",
                "LQD": "LQD",
                "HYG": "HYG",
                "USO": "USO"
            })
)
# 1.3 Macro: CPI level & Fed-Funds
fred = {"CPI": "CPIAUCSL", "FED": "FEDFUNDS"}
macro = pd.concat(
    [web.DataReader(code, "fred", START, END).rename(columns={code: name})
     for name, code in fred.items()],
    axis=1
).ffill()

macro["CPI_YoY"] = macro["CPI"].pct_change(12) * 100
macro["FED_4D"]  = macro["FED"].diff(4).clip(-0.25, 0.25)   # ±25 bp cap
macro_daily = macro.asfreq("D").ffill()

# ------------- 2. MERGE ------------------------------------
df = (
    pd.concat([portfolio_ret, hedge_ret], axis=1)
      .join(macro_daily[["CPI_YoY", "FED_4D"]], how="left")
      .ffill()
      .dropna()
)

# standardise macro shocks
df["CPI_SHOCK"] = (
    (df["CPI_YoY"] - df["CPI_YoY"].rolling(252).mean())
    / df["CPI_YoY"].rolling(252).std()
)
df["FED_SHOCK"] = df["FED_4D"] / df["FED_4D"].rolling(252).std()
df = df.dropna()

# ------------- 3. ROLLING BETAS & HEDGE WEIGHTS ------------
WIN = 63
betas_cpi, betas_fed = [], []
hr_t10, hr_dxy = [], []

for end in range(WIN, len(df)):
    w = df.iloc[end-WIN:end]

    # --- clean NaNs/±inf for regression --------------------
    w_clean = w[["PORT", "CPI_SHOCK", "FED_SHOCK"]].replace([np.inf, -np.inf], np.nan).dropna()
    if len(w_clean) >= 25:                   # need enough obs
        res = sm.OLS(w_clean["PORT"],
                     sm.add_constant(w_clean[["CPI_SHOCK", "FED_SHOCK"]])
                     ).fit()
        betas_cpi.append(res.params["CPI_SHOCK"])
        betas_fed.append(res.params["FED_SHOCK"])
    else:
        betas_cpi.append(np.nan)
        betas_fed.append(np.nan)

    # --- covariance hedge weights (unchanged) -------------
    cov_t10 = w[["PORT", "T10Y"]].cov().iloc[0, 1]
    var_t10 = w["T10Y"].var()
    beta_t10 = cov_t10 / var_t10
    if w[["PORT", "T10Y"]].corr().iloc[0, 1] > 0:
        beta_t10 *= -1                      # short bonds when corr positive

    cov_dxy  = w[["PORT", "DXY"]].cov().iloc[0, 1]
    beta_dxy = cov_dxy / w["DXY"].var()

    hr_t10.append(beta_t10)
    hr_dxy.append(beta_dxy)



idx = df.index[WIN:]
df.loc[idx, "BETA_CPI"] = betas_cpi
df.loc[idx, "BETA_FED"] = betas_fed
df.loc[idx, "HR_T10"]   = hr_t10
df.loc[idx, "HR_DXY"]   = hr_dxy

# ------------- 4. APPLY HEDGE & METRICS --------------------
df["HEDGED_RET"] = (
    df["PORT"]
    - df["HR_T10"].shift(1) * df["T10Y"]
    - df["HR_DXY"].shift(1) * df["DXY"]
)
# --- volatility-target overlay ---------------------------------
TARGET_FRAC = 0.80        # run at 80 % of original σ  ➜ ≈20 % cut
lookback    = 63          # 3-month rolling vol window

orig_sigma  = df["PORT"].rolling(lookback).std()
hedg_sigma  = df["HEDGED_RET"].rolling(lookback).std()

# scale factor so hedged σ → TARGET_FRAC × original σ
scale       = (TARGET_FRAC * orig_sigma / hedg_sigma).shift(1).clip(0, 3)
df["HEDGED_RET"] *= scale


vol_plain  = df["PORT"].std()       * np.sqrt(252)
vol_hedged = df["HEDGED_RET"].std() * np.sqrt(252)
reduction  = 100 * (1 - vol_hedged / vol_plain)

print("-"*42)
print("Dynamic Macro Hedge Results")
print(f"Annualised Vol (Original): {vol_plain:6.2%}")
print(f"Annualised Vol (Hedged) : {vol_hedged:6.2%}")
print(f"Volatility Reduction    : {reduction:6.1f}%")
print("-"*42)

# ------------- 5. PLOTS ------------------------------------
cum = (1 + df[["PORT", "HEDGED_RET"]]).cumprod()
cum.plot(figsize=(10,4), title="Cumulative Return: Portfolio vs Hedged")
plt.ylabel("Growth of $1")
plt.tight_layout(); plt.savefig(FIG_DIR/"cum_return.png", dpi=150)

df[["BETA_CPI", "BETA_FED"]].plot(figsize=(10,4),
                                  title="Rolling Macro Betas (CPI & Fed)")
plt.tight_layout(); plt.savefig(FIG_DIR/"rolling_macro_betas.png", dpi=150)

df[["HR_T10", "HR_DXY"]].plot(figsize=(10,4),
                              title="Rolling Hedge Weights")
plt.tight_layout(); plt.savefig(FIG_DIR/"hedge_weights.png", dpi=150)

realised = (
    df[["PORT", "HEDGED_RET"]]
      .rolling(63).std().mul(np.sqrt(252)).dropna()
)
realised.plot(figsize=(10,4), title="Realised Volatility (63-day)")
plt.tight_layout(); plt.savefig(FIG_DIR/"realised_vol.png", dpi=150)

def drawdown(s): return s / s.cummax() - 1
pd.DataFrame({
    "PORT":  drawdown(cum["PORT"]),
    "HEDGED":drawdown(cum["HEDGED_RET"])
}).plot(figsize=(10,4), title="Drawdowns")
plt.tight_layout(); plt.savefig(FIG_DIR/"drawdown.png", dpi=150)

print(f"Charts saved to: {FIG_DIR.resolve()}")
