#pragma once
#include <vector>
namespace sre {
class YieldCurve;
struct Cashflow { int days; double amount; };
class Instrument {
public:
    virtual ~Instrument() = default;
    virtual double npv(const YieldCurve&) const = 0;
    virtual std::vector<Cashflow> cashflows() const = 0;
};
}