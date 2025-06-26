# Asset Allocation Optimizer  
<sub>Rolling mean–variance portfolio with turnover & ESG constraints</sub>

## Overview
This project implements a **monthly‐rebalanced asset-allocation engine** that:

* Forecasts expected returns using trailing momentum (swap-in ML alpha easily)
* Estimates risk with a full sample covariance matrix
* Solves a convex mean–variance problem in **CVXPY** with  
  – long-only, 30 % position cap  
  – ≤ 5 % gross leverage  
  – ESG floor ≥ 0.65  
  – L¹ turnover penalty  
* Produces realistic back-test metrics (ann. ret ≈ 11.5 %, Sharpe ≈ 0.93)

Full details in [`notebooks/Asset_Allocation_Optimizer.ipynb`](notebooks/Asset_Allocation_Optimizer.ipynb).

---

## Quick Start

```bash
git clone https://github.com/<your-handle>/asset-allocation-optimizer.git
cd asset-allocation-optimizer
pip install -r requirements.txt
python src/optimizer.py          # runs the script version & saves figures

