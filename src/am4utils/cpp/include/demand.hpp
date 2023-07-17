#pragma once
#include <duckdb.hpp>

using std::string;
using std::to_string;

struct PaxDemand {
    uint16_t y;
    uint16_t j;
    uint16_t f;

    PaxDemand();
    PaxDemand(uint16_t y, uint16_t j, uint16_t f);

    static const string repr(const PaxDemand& demand);
};

struct CargoDemand {
    uint32_t l;
    uint32_t h;

    CargoDemand();
    CargoDemand(uint32_t l, uint32_t h);
    CargoDemand(const PaxDemand& pax_demand);

    static const string repr(const CargoDemand& demand);
};

#if BUILD_PYBIND == 1
#include "binder.hpp"

py::dict to_dict(const PaxDemand& ap);
py::dict to_dict(const CargoDemand& ap);
#endif