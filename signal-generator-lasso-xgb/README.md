# Execution-Aware Signal Generator (Lasso/XGBoost)

This project demonstrates a rolling-window machine learning pipeline for generating trading signals from financial time series. It simulates execution-aware long/short positioning using Lasso and XGBoost.

## Overview

- Uses synthetic or historical returns data
- Applies Lasso and XGBoost with walk-forward training
- Generates long/short signals
- Evaluates accuracy and plots strategy PnL

## Example

![Backtest Result](backtest_output.png)

## Files

- `signal_generator.py`: Main script for feature engineering, training, signal generation
- `backtest_output.png`: Strategy PnL vs baseline plot
- `sample_data.csv`: Optional sample input (if not generated on the fly)

## How to Run

```bash
python signal_generator.py
```

## Dependencies

- Python 3.9+
- pandas, numpy, sklearn, matplotlib, xgboost
