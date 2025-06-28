#pragma once
#include "Instrument.hpp"
namespace sre {
class Bond : public Instrument {
    double coupon_;
    int tenor_y_;
    int freq_;
    double face_{100.0};
public:
    Bond(double coupon,int tenorYears,int frequency=2);
    double npv(const YieldCurve&) const override;
    std::vector<Cashflow> cashflows() const override;
};
}