# 🧠 Dynamic Macro Hedge Model

This Python script constructs and evaluates a dynamically hedged macro portfolio using:
- **Inverse-volatility weighted portfolio** of SPY, QQQ, EEM, GLD
- **Macro factor betas** to CPI surprises and Fed Funds shocks
- **Covariance-based hedges** using 10-Year Treasury futures (`ZN=F`) and the Dollar Index (`DXY`)
- **Volatility targeting overlay** to maintain stable portfolio risk

It saves five plots to visualize cumulative return, betas, hedge weights, volatility, and drawdowns.

---

## 🔧 Methodology

- **Beta Estimation:** Rolling OLS regressions estimate sensitivity to macro shocks.
- **Shock Definitions:**
  - CPI shock = z-score of 12-month YoY CPI change
  - Fed shock = clipped 4-day change in Fed Funds rate
- **Hedging:** Uses rolling covariance to size positions in ZN and DXY to minimize risk exposure.
- **Volatility Targeting:** Scales exposure to keep realized vol at 80% of original level.

---

## 📈 Output Charts

Saved under the `/figures` directory:
- `cum_return.png`: Growth of $1 comparison
- `rolling_macro_betas.png`: Betas to CPI and Fed
- `hedge_weights.png`: T10Y and DXY hedge coefficients
- `realised_vol.png`: Rolling 63-day vol
- `drawdown.png`: Drawdown comparison

---

## 📦 Installation

```bash
pip install -r requirements.txt
```
