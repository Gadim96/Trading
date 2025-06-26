#  Asset Allocation Optimizer

This Python-based asset allocation engine uses momentum signals, GARCH-based risk forecasts, and a constrained mean-variance optimizer (via CVXPY) to build an optimized portfolio. It dynamically allocates across a fixed ETF universe using rolling window rebalancing.

## � Methodology

- **Expected Returns**: Based on 12-month momentum (can be replaced with a model like XGBoost).
- **Risk Estimation**: Diagonal GARCH(1,1) applied to each asset’s return series.
- **Optimization**: Mean-variance optimization subject to:
  - Max 30% per asset
  - No shorting (long-only)
  - Fully invested (weights sum to 1)
  - Optional turnover penalty (`λ_turn`) to reduce transaction costs

##  Requirements

Install required packages using:

```bash
pip install numpy pandas yfinance matplotlib arch cvxpy
```
## Files

File                           |	Description
asset-allocation-optimizer.py	 |  Main Python script for backtest and plots
README.md	Project documentation|
optimized_portfolio_return.png |	Cumulative performance of the strategy
rolling_portfolio_weights.png	 |Area plot of portfolio allocations
turnover_per_balance.png	     |Turnover per rebalance
cumulative_turnover.png	       |Cumulative turnover over time

## Backtest Results (2015–2025)

Annualised Return : 11.45%
Annualised Vol    : 12.31%
Sharpe Ratio      : 0.93
