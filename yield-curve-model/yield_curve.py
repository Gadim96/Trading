#!/usr/bin/env python3
"""
Yield-Curve Construction & Nelson-Siegel Fit (USD Treasuries)
------------------------------------------------------------
• Downloads latest par-yield data from FRED
• Bootstraps zero-coupon discount factors
• Fits Nelson-Siegel parameters (β0, β1, β2, τ)
• Saves interactive plots + PNG in /plots
"""

import os, datetime as dt
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import minimize
import pandas_datareader.data as web
from statsmodels.tsa.statespace.sarimax import SARIMAX

# ---------- 1. Download par-yield curve ----------
FRED_CODES = {
    "1M": "DGS1MO",  "3M": "DGS3MO",  "6M": "DGS6MO",
    "1Y": "DGS1",    "2Y": "DGS2",    "3Y": "DGS3",
    "5Y": "DGS5",    "7Y": "DGS7",    "10Y": "DGS10",
    "20Y": "DGS20",  "30Y": "DGS30",
}

def download_yields(start="2015-01-01"):
    end = dt.date.today()
    df_list = []
    for tenor, code in FRED_CODES.items():
        s = web.DataReader(code, "fred", start, end).rename(columns={code: tenor})
        df_list.append(s)
    df = pd.concat(df_list, axis=1).dropna(how="all")
    return df

# ---------- 2. Bootstrap zero-coupon curve ----------
def bootstrap_zero_curve(par_ylds):
    """Simple bootstrapping with ACT/365 and semi-annual coupons."""
    tenors = np.array([  1/12,  3/12,  6/12, 1, 2, 3, 5, 7, 10, 20, 30 ])
    par = par_ylds.values / 100      # convert % → decimal
    disc = np.empty_like(par)
    for i, T in enumerate(tenors):
        c = par[i] / 2 if T > 1 else 0  # coupon (semi-annual) except bills
        if i == 0:                      # 1-month bill → simple discount
            disc[i] = 1 / (1 + par[i] * T)
        else:
            pv_coupons = np.sum(disc[:i] * c)
            disc[i] = (1 - pv_coupons) / (1 + c)
    zero_rates = (disc**(-1/tenors) - 1)
    return pd.DataFrame(
        {"tenor": tenors, "zero_rate": zero_rates, "discount": disc}
    )

# ---------- 3. Nelson-Siegel fit ----------
def nelson_siegel(tau, beta0, beta1, beta2, m):
    return beta0 + beta1*((1-np.exp(-m/tau))/(m/tau)) + beta2*((1-np.exp(-m/tau))/(m/tau) - np.exp(-m/tau))

def fit_ns(zero_df):
    m = zero_df["tenor"].values
    y = zero_df["zero_rate"].values
    def err(theta):
        return np.sum((nelson_siegel(*theta, m) - y)**2)
    theta0 = (0.03, -0.02, 0.02, 1.0)  # (τ, β0, β1, β2)
    bounds = [(0.05, 5), (-0.1, 0.1), (-0.1, 0.1), (-0.1, 0.1)]
    res = minimize(err, x0=theta0, bounds=bounds, method="L-BFGS-B")
    τ, β0, β1, β2 = res.x
    fitted = nelson_siegel(τ, β0, β1, β2, m)
    zero_df["ns_fit"] = fitted
    zero_df.attrs["params"] = {"tau": τ, "beta0": β0, "beta1": β1, "beta2": β2}
    return zero_df

# ---------- 4. Plot ----------
def plot_curve(df):
    plt.figure()
    plt.plot(df["tenor"], df["zero_rate"]*100, "o-", label="Bootstrap ZC rate")
    plt.plot(df["tenor"], df["ns_fit"]*100, "s--", label="Nelson-Siegel fit")
    plt.xlabel("Maturity (years)")
    plt.ylabel("Yield (%)")
    plt.title("USD Zero-Coupon Yield Curve — {}".format(dt.date.today()))
    plt.legend()
    plt.grid(True)
    os.makedirs("plots", exist_ok=True)
    fname = f"plots/curve_{dt.date.today()}.png"
    plt.savefig(fname, dpi=300)
    print(f"✅ Plot saved to {fname}")


# ---------- 5. Kalman-filter factor forecast ----------
def build_ns_history(lookback_days=504):
    """Fit Nelson-Siegel to each day in the past 'lookback_days' and
    return a DataFrame of beta0, beta1, beta2."""
    start = (dt.date.today() - dt.timedelta(days=lookback_days * 1.4)).isoformat()
    df = download_yields(start)  # bigger window to survive NaNs
    df = df.dropna()
    betas = []
    for idx, row in df.iterrows():
        zc = bootstrap_zero_curve(row)
        zc = fit_ns(zc)
        p = zc.attrs["params"]
        betas.append([idx, p["beta0"], p["beta1"], p["beta2"]])
    hist = pd.DataFrame(betas, columns=["date", "beta0", "beta1", "beta2"]).set_index("date")
    hist = hist.last(f"{lookback_days}D")
    return hist


def kalman_ar1(series, steps=30):
    """AR(1) with Kalman filter for quick forecast & conf-int."""
    mod  = SARIMAX(series, order=(1,0,0), trend="n")
    res  = mod.fit(disp=False)
    pred = res.get_forecast(steps)
    return pred.predicted_mean

def forecast_curves(hist_betas, steps=30):
    f_beta0 = kalman_ar1(hist_betas["beta0"], steps)
    f_beta1 = kalman_ar1(hist_betas["beta1"], steps)
    f_beta2 = kalman_ar1(hist_betas["beta2"], steps)

    tenors  = np.array([0.5, 1, 2, 3, 5, 7, 10, 20, 30])
    curves  = {}
    for h in [9, 19, 29]:          # 10-, 20-, 30-day horizon (0-indexed)
        y = nelson_siegel(
            1.0,
            f_beta0.iloc[h],       # ← positional
            f_beta1.iloc[h],
            f_beta2.iloc[h],
            tenors,
        )
        curves[h + 1] = y
    return tenors, curves


def plot_forecast(tenors, curves, today_curve):
    plt.figure()
    plt.plot(tenors, today_curve*100, 'ko-', label="Today")
    colors = ["tab:blue", "tab:orange", "tab:green"]
    for (h, y), c in zip(curves.items(), colors):
        plt.plot(tenors, y*100, '--', label=f'+{h} days', color=c)
    plt.xlabel("Maturity (yrs)")
    plt.ylabel("Yield (%)")
    plt.title("Kalman-Filtered Nelson-Siegel Curve Forecasts")
    plt.legend()
    plt.grid(True)
    fname = f"plots/forecast_{dt.date.today()}.png"
    os.makedirs("plots", exist_ok=True)
    plt.savefig(fname, dpi=300)
    print(f"✅ Forecast plot saved to {fname}")

# ---------- 6. Pipeline ----------
def main():
    # 1) Try FRED live download
    try:
        yields = download_yields().iloc[-1]  # latest row
        print("🟢 Pulled latest yields from FRED")
    except Exception as e:
        print("🔴 FRED download failed → using local CSV")
        yields = pd.read_csv("data/treasury_yields.csv", index_col=0).iloc[-1]

    zero_df = bootstrap_zero_curve(yields)
    zero_df = fit_ns(zero_df)
    print("NS params:", zero_df.attrs["params"])
    plot_curve(zero_df)

    # ------- optional forecast ------
    hist = build_ns_history()
    tenors, curves = forecast_curves(hist)

    # slice today’s curve to the same 9 tenors (≥0.5y)
    today9 = zero_df.loc[zero_df["tenor"] >= 0.5, "ns_fit"].values
    plot_forecast(tenors, curves, today9)


if __name__ == "__main__":
    main()
