# Vendored Opus library
# Download from: https://opus-codec.org/

cmake_minimum_required(VERSION 3.20)
project(opus)

# This is a placeholder
# Real implementation would include full opus source tree
# For now, assume system opus is available

find_package(PkgConfig QUIET)
if(PKG_CONFIG_FOUND)
  pkg_check_modules(OPUS opus)
endif()

if(OPUS_FOUND)
  add_library(opus INTERFACE)
  target_include_directories(opus INTERFACE ${OPUS_INCLUDE_DIRS})
  target_link_libraries(opus INTERFACE ${OPUS_LIBRARIES})
else()
  message(FATAL_ERROR "Opus not found. Install libopus-dev or provide vendored source.")
endif()
