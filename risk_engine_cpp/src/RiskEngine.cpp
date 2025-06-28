#include "RiskEngine.hpp"
#include "Curve.hpp"
#include "Instrument.hpp"
namespace sre {
RiskEngine::RiskEngine(const YieldCurve& c,std::vector<std::shared_ptr<Instrument>> p):baseCurve_(c),portfolio_(std::move(p)){}
ScenarioResult RiskEngine::run(const Scenario& s) const{
    auto calc=[&](const YieldCurve& yc){double v=0;for(auto& i:portfolio_)v+=i->npv(yc);return v;};
    YieldCurve shock=baseCurve_.bumped(s.parallelShift_bp);
    double pv0=calc(baseCurve_), pv1=calc(shock);
    YieldCurve up=baseCurve_.bumped(1.0), down=baseCurve_.bumped(-1.0);
    double dv01=(calc(down)-calc(up))/2.0;
    double convex=(calc(up)+calc(down)-2*pv0);
    return {s.name,pv0,pv1,dv01,convex};
}
}