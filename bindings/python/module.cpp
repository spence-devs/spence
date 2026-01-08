#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

namespace py = pybind11;

void init_engine(py::module_&);
void init_player(py::module_&);
void init_track(py::module_&);

PYBIND11_MODULE(_native, m) {
    m.doc() = "Native audio engine for spence";
    
    init_engine(m);
    init_player(m);
    init_track(m);
}
