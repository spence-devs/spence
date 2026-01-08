#include <pybind11/pybind11.h>
#include "spence/engine.h"
#include "spence/node.h"

namespace py = pybind11;

void init_engine(py::module_& m) {
    py::class_<spence::NodeConfig>(m, "NodeConfig")
        .def(py::init<>())
        .def_readwrite("thread_pool_size", &spence::NodeConfig::thread_pool_size);
    
    py::class_<spence::Node>(m, "Node")
        .def(py::init<const spence::NodeConfig&>(),
             py::arg("config") = spence::NodeConfig{})
        .def("create_player", &spence::Node::create_player,
             py::call_guard<py::gil_scoped_release>());
}
