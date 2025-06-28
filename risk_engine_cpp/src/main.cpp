#include <iostream>
#include <memory>
#include "RiskEngine.hpp"
#include "Bond.hpp"
#include "Curve.hpp"
int main(){
    using namespace sre;
    YieldCurve curve({{0,1.0},{365,0.98},{365*5,0.90},{365*10,0.82}});
    auto b5=std::make_shared<Bond>(0.03,5,2);
    auto b10=std::make_shared<Bond>(0.04,10,2);
    RiskEngine eng(curve,{b5,b10});
    Scenario s{"+25bp",25.0};
    auto r=eng.run(s);
    std::cout<<r.name<<"\nPV:"<<r.pv_base<<"\nShocked:"<<r.pv_shocked<<"\nDV01:"<<r.dv01<<"\nConv:"<<r.convexity<<std::endl;
}
