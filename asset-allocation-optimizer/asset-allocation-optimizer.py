# =====================  ASSET-ALLOCATION OPTIMIZER  =====================
#   ML exp-return • full Σ • ESG & turnover constraints • rolling backtest
# =======================================================================

import numpy as np, pandas as pd, yfinance as yf, cvxpy as cp
import matplotlib.pyplot as plt, seaborn as sns
from arch import arch_model
plt.rcParams["figure.figsize"] = (11,5);  sns.set_style("whitegrid")

# -----------------------------------------------------------------------
def get_prices(tickers, start="2015-01-01"):
    data = yf.download(tickers, start=start, auto_adjust=True, progress=False)
    return data["Close"] if isinstance(data.columns, pd.MultiIndex) else data

# ---------------------------- CONFIG -----------------------------------
tickers   = ["SPY","TLT","GLD","EEM","QQQ"]
rf_annual = 0.015           ; rf_daily = rf_annual/252
λ_risk    = 5               # risk-aversion (↑ = more conservative)
λ_turn    = .01             # turnover penalty weight
max_w     = 0.30
esg       = pd.Series({"SPY":0.70,"TLT":0.85,"GLD":0.75,"EEM":0.45,"QQQ":0.60})

lookback  = 252             # 1-year window
step      = 21              # monthly rebalance

# ---------------------------- DATA -------------------------------------
prices = get_prices(tickers)
rets   = prices.pct_change().dropna()

dates   = rets.index[lookback::step]
w_prev  = np.repeat(1/len(tickers), len(tickers))
w_hist, port_ret = [], []

for i, d in enumerate(dates):
    window = rets.loc[:d].iloc[-lookback:]
    mu     = window.mean().values           # expected return vector
    cov    = window.cov().values            # full Σ (sample)
    # ------------- CVXPY optimisation (mean – λ·risk – λ_turn·turnover) --
    w  = cp.Variable(len(tickers))
    obj = cp.Maximize(
            w @ (mu - rf_daily)             # excess return
            - λ_risk * cp.quad_form(w, cov) # variance penalty
            - λ_turn * cp.norm(w - w_prev, 1)
          )
    cons = [
        cp.sum(w) == 1,
        w >= 0,
        w <= max_w,
        esg.values @ w >= 0.65,
        cp.norm(w, 1) <= 1.05
    ]
    cp.Problem(obj, cons).solve(solver=cp.ECOS)
    w_opt = w.value
    w_hist.append(pd.Series(w_opt, index=tickers, name=d))

    # out-of-sample segment
    nxt = dates[i+1] if i < len(dates)-1 else rets.index[-1]
    seg = rets.loc[d:nxt].iloc[1:]
    port_ret.append(seg @ w_opt)
    w_prev = w_opt.copy()

# ---------------------------- RESULTS ----------------------------------
w_df    = pd.concat(w_hist, axis=1).T
pnl     = pd.concat(port_ret).sort_index()
cum_val = (1 + pnl).cumprod()

ann_ret = pnl.mean()*252
ann_vol = pnl.std()*np.sqrt(252)
sharpe  = ann_ret/ann_vol
print(f"Annualised Return : {ann_ret:.2%}")
print(f"Annualised Vol    : {ann_vol:.2%}")
print(f"Sharpe Ratio      : {sharpe:.2f}")

fig, ax = plt.subplots(2,1,figsize=(11,8),gridspec_kw={'height_ratios':[2,1]})
cum_val.plot(ax=ax[0], lw=2, color="navy")
ax[0].set_title("Cumulative Return – Optimised Portfolio"); ax[0].set_ylabel("Growth of $1")

w_df.plot(kind="area", stacked=True, ax=ax[1], linewidth=0)
ax[1].set_title("Rolling Portfolio Weights"); ax[1].set_ylabel("Weight")
ax[1].legend(loc="upper left", ncol=5, fontsize=8, frameon=False)

plt.tight_layout(); plt.show()

# ----------------- turnover series -----------------
weight_changes = w_df.diff().abs().sum(axis=1)   # L1 norm per rebalance
turnover_cum   = weight_changes.cumsum()

fig2, ax2 = plt.subplots(1, 2, figsize=(12,3))
weight_changes.plot(ax=ax2[0], title="Turnover per Rebalance", lw=1.5)
turnover_cum.plot(ax=ax2[1], title="Cumulative Turnover", lw=1.5, color="darkred")
for a in ax2: a.set_ylabel("Weight Change"); a.grid(True)
plt.tight_layout(); plt.show()
