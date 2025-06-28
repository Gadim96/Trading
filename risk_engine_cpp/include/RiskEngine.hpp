#pragma once
#include <vector>
#include <memory>
#include "Scenario.hpp"
namespace sre {
class Instrument; class YieldCurve;
struct ScenarioResult {
    std::string name; double pv_base; double pv_shocked;
    double dv01; double convexity;
};
class RiskEngine {
    const YieldCurve& baseCurve_;
    std::vector<std::shared_ptr<Instrument>> portfolio_;
public:
    RiskEngine(const YieldCurve&,std::vector<std::shared_ptr<Instrument>>);
    ScenarioResult run(const Scenario&) const;
};
}