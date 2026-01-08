#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "spence/player.h"

namespace py = pybind11;

void init_player(py::module_& m) {
    py::enum_<spence::PlayerState>(m, "PlayerState")
        .value("IDLE", spence::PlayerState::Idle)
        .value("LOADING", spence::PlayerState::Loading)
        .value("READY", spence::PlayerState::Ready)
        .value("PLAYING", spence::PlayerState::Playing)
        .value("PAUSED", spence::PlayerState::Paused)
        .value("STOPPED", spence::PlayerState::Stopped);
    
    py::class_<spence::PlayerMetrics>(m, "PlayerMetrics")
        .def(py::init<>())
        .def_readonly("frames_generated", &spence::PlayerMetrics::frames_generated)
        .def_readonly("frames_dropped", &spence::PlayerMetrics::frames_dropped)
        .def_readonly("decode_errors", &spence::PlayerMetrics::decode_errors)
        .def_readonly("buffer_underruns", &spence::PlayerMetrics::buffer_underruns)
        .def_readonly("avg_frame_time_us", &spence::PlayerMetrics::avg_frame_time_us);
    
    py::class_<spence::Player, std::shared_ptr<spence::Player>>(m, "Player")
        .def("load", &spence::Player::load,
             py::call_guard<py::gil_scoped_release>())
        .def("play", &spence::Player::play,
             py::call_guard<py::gil_scoped_release>())
        .def("pause", &spence::Player::pause,
             py::call_guard<py::gil_scoped_release>())
        .def("stop", &spence::Player::stop,
             py::call_guard<py::gil_scoped_release>())
        .def("seek", &spence::Player::seek,
             py::call_guard<py::gil_scoped_release>())
        .def("set_volume", &spence::Player::set_volume,
             py::call_guard<py::gil_scoped_release>())
        .def("read_frame", [](spence::Player& self) -> py::bytes {
            uint8_t buffer[4000];
            size_t written = 0;
            
            py::gil_scoped_release release;
            bool success = self.read_frame(buffer, sizeof(buffer), written);
            py::gil_scoped_acquire acquire;
            
            if (!success || written == 0) {
                return py::bytes();
            }
            return py::bytes(reinterpret_cast<const char*>(buffer), written);
        })
        .def_property_readonly("position_ms", &spence::Player::position_ms)
        .def_property_readonly("state", &spence::Player::state)
        .def("metrics", &spence::Player::metrics,
             py::call_guard<py::gil_scoped_release>());
}
