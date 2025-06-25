#!/usr/bin/env python3
"""
Macro–Factor Yield-Curve Analyzer (one-file, interactive).
Explains movements in the 10Y US Treasury yield and the 10Y–2Y curve slope
using CPI, Unemployment, and Fed Funds as predictors. Adds confidence bands.
"""

import datetime as dt, numpy as np, pandas as pd
import matplotlib.pyplot as plt, statsmodels.api as sm
import pandas_datareader.data as web

# ─── 1. Download ─────────────────────────────────────────────────────────
MACRO = {"CPI": "CPIAUCSL", "UNRATE": "UNRATE", "FEDFUNDS": "FEDFUNDS"}
YLD   = {"2Y": "DGS2", "10Y": "DGS10"}
START = "2005-01-01"; END = dt.date.today()

def fetch(codes):
    dfs = [web.DataReader(c, "fred", START, END).rename(columns={c: n})
           for n, c in codes.items()]
    df  = pd.concat(dfs, axis=1)
    return df.asfreq("D").ffill()          # forward-fill to daily grid

macro  = fetch(MACRO)
yields = fetch(YLD)

df = macro.join(yields, how="outer").ffill().dropna()

# ─── 2. Curve metrics ────────────────────────────────────────────────────
df["Slope_10y_2y"] = df["10Y"] - df["2Y"]

# ─── 3. Rolling OLS ──────────────────────────────────────────────────────
TARGETS, WIN = ["10Y", "Slope_10y_2y"], 252
print(f"Data rows: {len(df)}, rolling window: {WIN}")

for tgt in TARGETS:
    y = df[tgt]
    X = sm.add_constant(df[["CPI", "UNRATE", "FEDFUNDS"]])
    r2, beta, beta_lo, beta_hi = [np.nan]*WIN, [np.nan]*WIN, [np.nan]*WIN, [np.nan]*WIN

    for i in range(WIN, len(df)):
        res = sm.OLS(y.iloc[i-WIN:i], X.iloc[i-WIN:i]).fit()
        b = res.params["CPI"]
        se = res.bse["CPI"]
        r2.append(res.rsquared)
        beta.append(b)
        beta_lo.append(b - 1.96 * se)
        beta_hi.append(b + 1.96 * se)

    df[f"{tgt}_R2"]               = r2
    df[f"{tgt}_β_CPI"]            = beta
    df[f"{tgt}_β_CPI_lower"]      = beta_lo
    df[f"{tgt}_β_CPI_upper"]      = beta_hi

# ─── 4. Plot with optional CI band ───────────────────────────────────────
def show(series, title, ylabel="", lower=None, upper=None):
    plt.figure()
    series.plot(label="β(CPI)", lw=1.8)
    if lower is not None and upper is not None:
        plt.fill_between(series.index, lower, upper, color="gray", alpha=0.3, label="95% CI")
    plt.title(title)
    plt.ylabel(ylabel)
    plt.grid(True)
    plt.tight_layout()
    plt.legend()
    plt.show()

show(df["10Y_R2"],            "Rolling R² – 10-Year Yield")
show(df["Slope_10y_2y_R2"],   "Rolling R² – 10Y-2Y Slope")
show(df["10Y_β_CPI"],         "β₍CPI₎ – 10-Year Yield",       "Coefficient",
     lower=df["10Y_β_CPI_lower"], upper=df["10Y_β_CPI_upper"])
show(df["Slope_10y_2y_β_CPI"],"β₍CPI₎ – 10Y–2Y Slope",         "Coefficient",
     lower=df["Slope_10y_2y_β_CPI_lower"], upper=df["Slope_10y_2y_β_CPI_upper"])

