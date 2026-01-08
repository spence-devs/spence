#pragma once

#include <string>
#include <cstdint>

namespace spence {

struct TrackInfo {
    std::string stream_url;
    uint64_t duration_ms = 0;
    uint32_t sample_rate = 48000;
    uint8_t channels = 2;
    
    bool is_valid() const {
        return !stream_url.empty() && duration_ms > 0;
    }
};

}
