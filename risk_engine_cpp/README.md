# Scenario Risk Engine (C++)

A modular C++ risk engine that simulates yield curve scenarios and revalues fixed-income instruments such as bonds. Includes Xcode support and unit tests using Catch2.

## 📌 Features

- 🔧 Modular C++ design (header/source split)
- 📈 Interest rate scenario simulation
- 🧮 Pricing of zero-coupon bonds
- 🧪 Unit testing with Catch2
- ⚙️ Cross-platform CMake build with Xcode support

---

## 🗂️ Project Structure
risk_engine_cpp/
├── include/
│ ├── Bond.hpp # Bond instrument definition
│ ├── Curve.hpp # Yield curve data
│ ├── Instrument.hpp # Base class for financial instruments
│ ├── RiskEngine.hpp # Scenario engine for pricing under curve shifts
│ └── Scenario.hpp # Shocked scenario representation
├── src/
│ └── Bond.cpp # Implementation of bond pricing
├── tests/
│ └── test_simple.cpp # Unit test using Catch2
├── CMakeLists.txt # CMake configuration
└── README.md # Project documentation
