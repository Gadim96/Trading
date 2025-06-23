# Execution-Aware Signal Generator (Lasso/XGBoost)

This project demonstrates a rolling-window machine learning pipeline for generating trading signals from financial time series data. It simulates execution-aware long/short positioning using Lasso and XGBoost models.

## Overview

- Fetches historical crypto data (Binance)
- Extracts predictive features including volatility, momentum, GARCH
- Trains models (Lasso or XGBoost) using walk-forward validation
- Generates 3-class directional signals: Down, Flat, Up
- Evaluates predictive accuracy and compares volatility forecasts

---

## 🧠 Feature Engineering

- Realized & GARCH volatility
- Momentum, Z-scores, imbalance
- RSI, MACD, signed volume
- Rolling-window standardization

Implemented in [`feaeture_engineering.py`](feaeture_engineering.py)

---

## 🔍 Volatility Forecast Example

GARCH model fitted to log returns and compared against realized volatility.

![GARCH Forecast Plot](garch_plot.png)

---

## 🎯 XGBoost Model Evaluation

Rolling 3-class XGBoost classifier trained on engineered features.

![XGBoost Evaluation](model_evaluation.png)

---

## 📁 File Guide

| File | Description |
|------|-------------|
| `fetch_data.py` | Pulls historical Binance futures data |
| `feaeture_engineering.py` | Constructs predictive features for ML |
| `xgboost_signal_generator.py` | Builds rolling XGBoost model and generates signals |
| `model_evaluation.png` | Evaluation screenshot for 3-class classifier |
| `garch_plot.png` | Volatility forecast vs realized vol plot |

---

## ▶️ How to Run

```bash
python fetch_data.py
python feauture_engineering.py
python xgboost_signal_generator.py
```

## 🔧 Dependencies

- Python 3.9+
- pandas
- numpy
- matplotlib
- scikit-learn
- xgboost
- arch
- python-binance

## Backtester

This project includes a custom backtester (`backtester.py`) that simulates realistic execution logic for long/short strategies. Key features include:

- ATR or volatility-based entry filtering
- Dynamic stop-loss / take-profit
- Randomized resolution of ambiguous bars (when both stop and target are hit)
- Maker fees and leverage impact
- Metrics: win rate, drawdown, PnL, ambiguity
# Execution-Aware Signal Generator

A modular backtesting engine for directional trading signals, designed for high-frequency environments with realistic execution constraints such as **latency**, **spread**, and **ambiguous bars**. Built to evaluate signal quality under execution-aware assumptions, simulating realistic market conditions.

## 🔍 Features

- **Rolling Signal Engine** with Lasso/XGBoost compatibility
- **Execution-aware backtest**:
  - Simulates delayed entries (`MAX_WAIT_BARS`)
  - Models spread and ambiguous bar outcomes (SL/TP touched in same bar)
- **ATR/Volatility Filters** to adapt entry/exit thresholds
- **Trade-by-trade accounting** of PnL, balance, drawdown
- **Metrics**: Final balance, win rate, drawdown, ambiguous trade rate

## 📈 Example Output

![Equity Curve](plots/equity_curve.png)

## 🧪 Usage

```bash
# Install dependencies
pip install -r requirements.txt

# Run backtest on sample data
python backtest.py
```

**Example output:**

![Backtest Result](backtest_equity_curve.png)



## 📌 Notes

- Rolling-window logic avoids lookahead bias
- Feature engineering is modular — extendable for new signals
- GARCH fitting can be slow; consider reducing rolling window for faster runs
- Backtest logic not included here — can be added using `backtrader`, `bt`, or custom code
