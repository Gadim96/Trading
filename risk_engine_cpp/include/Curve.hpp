#pragma once
#include <map>
#include <chrono>
namespace sre {
using Date = std::chrono::sys_days;
class YieldCurve {
    std::map<int,double> df_;
public:
    explicit YieldCurve(std::map<int,double> df);
    double discountFactor(int days) const;
    double zeroRate(int days) const;
    YieldCurve bumped(double shift_bp) const;
};
}