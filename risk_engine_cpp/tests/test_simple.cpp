#define CATCH_CONFIG_MAIN
#include <catch2/catch_test_macros.hpp>  
#include "Bond.hpp"
#include "Curve.hpp"
TEST_CASE("PV positive"){ using namespace sre; YieldCurve c({{0,1.0},{365,0.99}}); auto b=Bond(0.05,1,2); REQUIRE(b.npv(c)>0);}
