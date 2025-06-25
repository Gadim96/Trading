# Macro–Factor Yield-Curve Analyzer

This tool performs a rolling regression analysis to explain movements in US Treasury yields using macroeconomic variables.

## 📈 Overview

- **Targets:**  
  - 10-Year Treasury Yield (`DGS10`)  
  - Yield Curve Slope (`DGS10 - DGS2`)

- **Explanatory Variables:**  
  - Consumer Price Index (CPI)  
  - Unemployment Rate  
  - Federal Funds Rate

- **Method:**  
  - Rolling 252-day Ordinary Least Squares (OLS) regressions
  - Captures time-varying relationships between macro factors and yields

## 🔍 Outputs

- **Rolling R²**: How well macro variables explain each target over time
- **Rolling β(CPI)**: Coefficient on CPI with 95% confidence intervals
## 📊 Sample Plots

### Rolling R²
**10-Year Yield**
![r2-10-year](r2-10-year-yield.png)

**10Y–2Y Slope**
![r2-slope](rolling-r2-10Y-2Yyear.png)

### β(CPI) Coefficient
**10-Year Yield**
![beta-10y](10-year-yield.png)

**10Y–2Y Slope**
![beta-slope](10Y-2Y.png)

## 🛠️ Usage

```bash
pip install pandas numpy statsmodels matplotlib pandas_datareader
python macro_curve_analyzer.py

