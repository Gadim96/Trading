#include "Curve.hpp"
#include <cmath>
namespace sre {
YieldCurve::YieldCurve(std::map<int,double> df):df_(std::move(df)){}
double YieldCurve::discountFactor(int days) const{
    auto it=df_.lower_bound(days);
    if(it==df_.end()) return std::prev(df_.end())->second;
    return it->second;
}
double YieldCurve::zeroRate(int days) const{
    double df=discountFactor(days); double t=days/365.0;
    return -std::log(df)/t;
}
YieldCurve YieldCurve::bumped(double shift_bp) const{
    std::map<int,double> out;
    double f=std::exp(-shift_bp*1e-4);
    for(auto& [d,df]:df_) out[d]=df*f;
    return YieldCurve{out};
}
}