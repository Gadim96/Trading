#!/usr/bin/env python3
"""
Vanilla USD SOFR Swap Pricer
----------------------------
• Downloads latest par yields from FRED
• Bootstraps discount factors
• Prices a 5-year fixed-for-float swap
• Reports PV, fair par rate, DV01
• Plots PV vs. ±100 bp parallel curve shifts
"""

import os, datetime as dt
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
import pandas_datareader.data as web

# ──────────────────────────────────────────────────────────
# 1) Yield-curve download & bootstrap
# ──────────────────────────────────────────────────────────
FRED_CODES = {
    "1M": "DGS1MO", "3M": "DGS3MO", "6M": "DGS6MO",
    "1Y": "DGS1",   "2Y": "DGS2",   "3Y": "DGS3",
    "5Y": "DGS5",   "7Y": "DGS7",   "10Y": "DGS10",
    "20Y": "DGS20", "30Y": "DGS30",
}
TENORS_YRS = np.array([1/12, 3/12, 6/12, 1, 2, 3, 5, 7, 10, 20, 30])

def download_par_yields():
    end   = dt.date.today()
    start = end - dt.timedelta(days=30)          # only need recent data
    dfs   = [web.DataReader(code, "fred", start, end).rename(columns={code: t})
             for t, code in FRED_CODES.items()]
    return pd.concat(dfs, axis=1).ffill().iloc[-1] / 100  # % → decimal

def bootstrap_df(par):
    """Bootstraps discount factors under ACT/365, semi-annual coupons."""
    disc = np.empty_like(par)
    for i, (T, y) in enumerate(zip(TENORS_YRS, par)):
        c = 0 if T <= 0.5 else y / 2            # bills carry no coupon
        if i == 0:
            disc[i] = 1 / (1 + y * T)
        else:
            pv_cpn  = np.sum(disc[:i] * c)
            disc[i] = (1 - pv_cpn) / (1 + c)
    return pd.Series(disc, index=TENORS_YRS, name="DF")

# ──────────────────────────────────────────────────────────
# 2) Forward curve helper
# ──────────────────────────────────────────────────────────
def forwards_from_df(df_series, freq=2):
    """Simple-discrete forwards implied from discount factors."""
    times = df_series.index.to_numpy()
    dfs   = df_series.to_numpy()
    fwd   = np.empty_like(dfs)

    # First point (bill) — treat as simple yield
    fwd[0] = (1 / dfs[0] - 1) * freq

    # Remaining: f(t-1)/f(t)
    for i in range(1, len(dfs)):
        dt    = times[i] - times[i-1]
        fwd[i] = (dfs[i-1] / dfs[i] - 1) / dt
    return pd.Series(fwd, index=df_series.index, name="FWD")

# ──────────────────────────────────────────────────────────
# 3) Swap cash-flow schedule
# ──────────────────────────────────────────────────────────
def generate_schedule(years, freq=2):
    """Return year-fractions of payment dates."""
    periods = int(years * freq)
    return np.arange(1, periods + 1) / freq  # 0.5, 1.0, …

# ──────────────────────────────────────────────────────────
# 4) Pricing utilities
# ──────────────────────────────────────────────────────────
def interpolate(series, times):
    return np.interp(times, series.index, series.values)

def price_swap(notional, fixed_rate, df_series, fwd_series, times, delta=0.5):
    df   = interpolate(df_series, times)
    fwd  = interpolate(fwd_series, times)
    pv_fxd = notional * fixed_rate * delta * np.sum(df)
    pv_flt = notional * delta * np.sum(df * fwd)
    return pv_flt - pv_fxd, pv_fxd, pv_flt

def fair_rate(df_series, fwd_series, times, delta=0.5):
    df  = interpolate(df_series, times)
    fwd = interpolate(fwd_series, times)
    return np.sum(df * fwd) / np.sum(df)

def dv01(notional, fixed_rate, df_series, times, bump=1e-4):
    bumped_df  = df_series * np.exp(-bump * df_series.index)
    fwd        = forwards_from_df(df_series)
    fwd_bumped = forwards_from_df(bumped_df)

    pv_base, *_ = price_swap(notional, fixed_rate, df_series, fwd, times)
    pv_bump, *_ = price_swap(notional, fixed_rate, bumped_df, fwd_bumped, times)
    return (pv_bump - pv_base) / bump / notional

# ──────────────────────────────────────────────────────────
# 5) Main pipeline
# ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    par   = download_par_yields()
    disc  = bootstrap_df(par)
    fwd   = forwards_from_df(disc)

    # --- Swap parameters ---
    notional    = 100_000_000        # $100 mm
    maturity    = 5                  # 5-year swap
    fixed_rate  = 0.025              # 2.50% coupon
    pay_times   = generate_schedule(maturity)   # 0.5, 1.0, …

    # --- Price & analytics ---
    pv, pv_fixed, pv_float = price_swap(notional, fixed_rate, disc, fwd, pay_times)
    par_rate  = fair_rate(disc, fwd, pay_times)
    dv01_val  = dv01(notional, fixed_rate, disc, pay_times)

    print(f"\nSwap PV         : {pv/1e6: .2f} mm USD")
    print(f"  > PV of fixed : {pv_fixed/1e6: .2f} mm")
    print(f"  > PV of float : {pv_float/1e6: .2f} mm")
    print(f"Fair par rate   : {par_rate*100:.3f}%")
    print(f"DV01 (per $1)   : {dv01_val/1e4:.6f}")

    # --- PV vs. parallel shift plot ---
    shifts = np.linspace(-0.01, 0.01, 41)           # −100 → +100 bp
    pvs = []
    for s in shifts:
        bumped_df  = disc * np.exp(-s * disc.index)
        fwd_bumped = forwards_from_df(bumped_df)
        pv_shift, *_ = price_swap(notional, fixed_rate, bumped_df, fwd_bumped, pay_times)
        pvs.append(pv_shift / 1e6)

    plt.figure()
    plt.plot(shifts * 1e4, pvs)
    plt.axhline(0, lw=0.8, ls="--", c="k")
    plt.xlabel("Parallel Shift (bp)")
    plt.ylabel("Swap PV (mm USD)")
    plt.title("Swap PV vs. Parallel Curve Shift")
    plt.grid(True)
    os.makedirs("plots", exist_ok=True)
    plt.savefig("plots/pv_vs_shift.png", dpi=300)
    print(" PV-vs-shift plot saved to plots/pv_vs_shift.png")

