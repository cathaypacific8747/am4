#include "include/demand.hpp"
#include <cmath>

PaxDemand::PaxDemand() : y(0), j(0), f(0) {}
PaxDemand::PaxDemand(uint16_t y, uint16_t j, uint16_t f) : y(y), j(j), f(f) {}

PaxDemand PaxDemand::operator/(double load) const {
    return PaxDemand(
        static_cast<uint16_t>(floor(static_cast<double>(y) / load)),
        static_cast<uint16_t>(floor(static_cast<double>(j) / load)),
        static_cast<uint16_t>(floor(static_cast<double>(f) / load))
    );
}

CargoDemand::CargoDemand() : l(0), h(0) {}
CargoDemand::CargoDemand(uint32_t l, uint32_t h) : l(l), h(h) {}
CargoDemand::CargoDemand(const PaxDemand& pax_demand) :
    l(static_cast<uint32_t>(round(pax_demand.y / 2.0) * 1000)),
    h(pax_demand.j * 1000)
{}

CargoDemand CargoDemand::operator/(double load) const {
    return CargoDemand(
        static_cast<uint32_t>(floor(static_cast<double>(l) / load)),
        static_cast<uint32_t>(floor(static_cast<double>(h) / load))
    );
}

const string PaxDemand::repr(const PaxDemand& demand) {
    return "<PaxDemand " + to_string(demand.y) + "|" + to_string(demand.j) + "|" + to_string(demand.f) + ">";
}

const string CargoDemand::repr(const CargoDemand& demand) {
    return "<CargoDemand " + to_string(demand.l) + "|" + to_string(demand.h) + ">";
}

#if BUILD_PYBIND == 1
#include "include/binder.hpp"

py::dict to_dict(const PaxDemand& pd) {
    return py::dict(
        "y"_a=pd.y,
        "j"_a=pd.j,
        "f"_a=pd.f
    );
}

py::dict to_dict(const CargoDemand& cd) {
    return py::dict(
        "l"_a=cd.l,
        "h"_a=cd.h
    );
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
        .def("to_dict", py::overload_cast<const PaxDemand&>(&to_dict));
    
    py::class_<CargoDemand>(m_demand, "CargoDemand")
        .def(py::init<>())
        .def(py::init<int, int>(), "l"_a, "h"_a)
        .def(py::init<const PaxDemand&>(), "pax_demand"_a)
        .def_readonly("l", &CargoDemand::l)
        .def_readonly("h", &CargoDemand::h)
        .def("__repr__", &CargoDemand::repr)
        .def("to_dict", py::overload_cast<const CargoDemand&>(&to_dict));
}
#endif