# Derivatives Pricer (C++)

This is a simple C++ pricing engine for caplets using Black’s model.  
The tool reads a CSV file containing a discount curve and caplet definitions, and outputs price, delta, and vega for each instrument.

---

## 📌 Example Input Format: `market_data.csv`

```csv
maturity,zero_rate
0.5,0.03
1,0.032
2,0.035
5,0.04
10,0.042

T,F,K,sigma,tau
2,0.037,0.04,0.25,0.5
3,0.038,0.04,0.24,0.5
