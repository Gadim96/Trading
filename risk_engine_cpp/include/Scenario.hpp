#pragma once
#include <string>
namespace sre {
struct Scenario {
    std::string name;
    double parallelShift_bp{0.0};
};
}