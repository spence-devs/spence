# Vendored Ogg library
# Download from: https://xiph.org/ogg/

cmake_minimum_required(VERSION 3.20)
project(ogg)

find_package(PkgConfig QUIET)
if(PKG_CONFIG_FOUND)
  pkg_check_modules(OGG ogg)
endif()

if(OGG_FOUND)
  add_library(ogg INTERFACE)
  target_include_directories(ogg INTERFACE ${OGG_INCLUDE_DIRS})
  target_link_libraries(ogg INTERFACE ${OGG_LIBRARIES})
else()
  message(FATAL_ERROR "Ogg not found. Install libogg-dev or provide vendored source.")
endif()
