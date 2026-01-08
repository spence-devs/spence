cmake_minimum_required(VERSION 3.20)
project(spence_native VERSION 0.1.0 LANGUAGES CXX C)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

# Find or build vendored dependencies
add_subdirectory(thirdparty/opus)
add_subdirectory(thirdparty/libogg)
add_subdirectory(thirdparty/libsamplerate)

# Native library sources
set(SPENCE_SOURCES
    src/api.cpp
    src/engine.cpp
    src/node.cpp
    src/player.cpp
    src/track.cpp
    src/audio/decoder.cpp
    src/audio/encoder.cpp
    src/audio/resampler.cpp
    src/stream/opusstream.cpp
    src/stream/rtppacket.cpp
    src/extract/youtube.cpp
    src/extract/webm.cpp
    src/extract/mp4.cpp
)

add_library(spence_native STATIC ${SPENCE_SOURCES})

target_include_directories(spence_native
  PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    $<INSTALL_INTERFACE:include>
  PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/thirdparty/opus/include
    ${CMAKE_CURRENT_SOURCE_DIR}/thirdparty/libogg/include
    ${CMAKE_CURRENT_SOURCE_DIR}/thirdparty/libsamplerate/include
)

target_link_libraries(spence_native
  PUBLIC
    opus
    ogg
    samplerate
)

target_compile_options(spence_native PRIVATE
  $<$<CXX_COMPILER_ID:GNU,Clang>:-Wall -Wextra -O3>
  $<$<CXX_COMPILER_ID:MSVC>:/W4 /O2>
)

# Install rules
install(TARGETS spence_native
  EXPORT spence-targets
  ARCHIVE DESTINATION lib
  LIBRARY DESTINATION lib
  RUNTIME DESTINATION bin
)

install(DIRECTORY include/spence DESTINATION include)
