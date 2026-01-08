cmake_minimum_required(VERSION 3.20)
project(spence_bindings)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find Python
find_package(Python COMPONENTS Interpreter Development REQUIRED)

# Add pybind11
add_subdirectory(${CMAKE_CURRENT_SOURCE_DIR}/../native/thirdparty/pybind11 pybind11)

# Add native library
add_subdirectory(${CMAKE_CURRENT_SOURCE_DIR}/../native native)

# Python module
pybind11_add_module(_native
    python/module.cpp
    python/engine.cpp
    python/player.cpp
    python/track.cpp
)

target_link_libraries(_native PRIVATE spence_native)

target_include_directories(_native PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../native/include
)

# Set output name and location
set_target_properties(_native PROPERTIES
    OUTPUT_NAME "_native"
    PREFIX ""
)

# Install to Python package
install(TARGETS _native LIBRARY DESTINATION client/bridge)
