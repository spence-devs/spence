#include <pybind11/pybind11.h>
#include "spence/track.h"

namespace py = pybind11;

void init_track(py::module_& m) {
    py::class_<spence::TrackInfo>(m, "TrackInfo")
        .def(py::init<>())
        .def_readwrite("stream_url", &spence::TrackInfo::stream_url)
        .def_readwrite("duration_ms", &spence::TrackInfo::duration_ms)
        .def_readwrite("sample_rate", &spence::TrackInfo::sample_rate)
        .def_readwrite("channels", &spence::TrackInfo::channels)
        .def("is_valid", &spence::TrackInfo::is_valid);
}
