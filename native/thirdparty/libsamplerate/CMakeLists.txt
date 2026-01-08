# Vendored libsamplerate
# Download from: https://github.com/libsndfile/libsamplerate

cmake_minimum_required(VERSION 3.20)
project(samplerate)

find_package(PkgConfig QUIET)
if(PKG_CONFIG_FOUND)
  pkg_check_modules(SAMPLERATE samplerate)
endif()

if(SAMPLERATE_FOUND)
  add_library(samplerate INTERFACE)
  target_include_directories(samplerate INTERFACE ${SAMPLERATE_INCLUDE_DIRS})
  target_link_libraries(samplerate INTERFACE ${SAMPLERATE_LIBRARIES})
else()
  message(FATAL_ERROR "Samplerate not found. Install libsamplerate0-dev or provide vendored source.")
endif()
