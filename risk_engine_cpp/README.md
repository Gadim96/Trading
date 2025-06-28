# Scenario Risk Engine (C++)

A modular C++ risk engine that simulates yield curve scenarios and revalues fixed-income instruments such as bonds. Includes Xcode support and unit tests using Catch2.

## 📌 Features

- 🔧 Modular C++ design (header/source split)
- 📈 Interest rate scenario simulation
- 💵 Pricing of zero-coupon bonds
- 🧪 Unit testing with Catch2
- ⚙️ Cross-platform CMake build with Xcode support

---

## 🧠 Future Extensions

- Multi-curve interest rate models
- Additional instrument types (e.g., FRNs, swaps)
- Real market data integration
- Parallelized scenario generation

---

## 📝 Notes

- I ran the project using Xcode. Simply add all files to a new Xcode project. It should compile and run without issues.
- To run the tests, switch the scheme to the `tests` target in Xcode.

---

## 🔧 Manual Build with CMake (Optional)

```bash
cd risk_engine_cpp
cmake -B build
cmake --build build
./build/tests/test_simple
```

## Project Structure

risk_engine_cpp/
├── include/
│   ├── Bond.hpp
│   ├── Curve.hpp
│   ├── Instrument.hpp
│   ├── RiskEngine.hpp
│   └── Scenario.hpp
├── src/
│   └── Bond.cpp
├── tests/
│   └── test_simple.cpp
├── CMakeLists.txt
└── README.md
