#include "Bond.hpp"
#include "Curve.hpp"
namespace sre {
Bond::Bond(double c,int tenor,int f):coupon_(c),tenor_y_(tenor),freq_(f){}
std::vector<Cashflow> Bond::cashflows() const{
    std::vector<Cashflow> v;int periods=tenor_y_*freq_;
    double coup=coupon_/freq_*face_;
    for(int i=1;i<=periods;++i){
        int days=int(365.0/freq_*i); v.push_back({days,coup});
    } v.back().amount+=face_; return v;
}
double Bond::npv(const YieldCurve& yc) const{
    double pv=0; for(auto& cf:cashflows()) pv+=cf.amount*yc.discountFactor(cf.days);
    return pv;
}
}