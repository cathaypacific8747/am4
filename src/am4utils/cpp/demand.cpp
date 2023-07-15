#include "include/demand.hpp"
#include <cmath>

PaxDemand::PaxDemand() : y(0), j(0), f(0) {};
PaxDemand::PaxDemand(uint16_t y, uint16_t j, uint16_t f) : y(y), j(j), f(f) {};
PaxDemand::PaxDemand(const duckdb::unique_ptr<duckdb::DataChunk>& chunk, idx_t row) :
    y(chunk->GetValue(0, row).GetValue<uint16_t>()),
    j(chunk->GetValue(1, row).GetValue<uint16_t>()),
    f(chunk->GetValue(2, row).GetValue<uint16_t>()) {};

CargoDemand::CargoDemand() : l(0), h(0) {};
CargoDemand::CargoDemand(uint32_t l, uint32_t h) : l(l), h(h) {};
CargoDemand::CargoDemand(const PaxDemand& pax_demand) : l(lround(pax_demand.y / 2.0F) * 1000), h(pax_demand.j * 1000) {};


const string PaxDemand::repr(const PaxDemand& demand) {
    return "<PaxDemand " + to_string(demand.y) + "|" + to_string(demand.j) + "|" + to_string(demand.f) + ">";
};

const string CargoDemand::repr(const CargoDemand& demand) {
    return "<CargoDemand " + to_string(demand.l) + "|" + to_string(demand.h) + ">";
};

#if BUILD_PYBIND == 1
#include "include/binder.hpp"

py::dict pax_demand_to_dict(const PaxDemand& pd) {
    py::dict d(
        "y"_a=pd.y,
        "j"_a=pd.j,
        "f"_a=pd.f
    );
    return d;
}

py::dict cargo_demand_to_dict(const CargoDemand& cd) {
    py::dict d(
        "l"_a=cd.l,
        "h"_a=cd.h
    );
    return d;
}

void pybind_init_demand(py::module_& m) {
    py::module_ m_demand = m.def_submodule("demand");
    
    py::class_<PaxDemand>(m_demand, "PaxDemand")
        .def(py::init<>())
        .def(py::init<int, int, int>(), "y"_a, "j"_a, "f"_a)
        .def_readonly("y", &PaxDemand::y)
        .def_readonly("j", &PaxDemand::j)
        .def_readonly("f", &PaxDemand::f)
        .def("__repr__", &PaxDemand::repr)
        .def("to_dict", &pax_demand_to_dict);
    
    py::class_<CargoDemand>(m_demand, "CargoDemand")
        .def(py::init<>())
        .def(py::init<int, int>(), "l"_a, "h"_a)
        .def(py::init<const PaxDemand&>(), "pax_demand"_a)
        .def_readonly("l", &CargoDemand::l)
        .def_readonly("h", &CargoDemand::h)
        .def("__repr__", &CargoDemand::repr)
        .def("to_dict", &cargo_demand_to_dict);
}
#endif