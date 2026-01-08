#pragma once

#include <string>
#include <cstdint>

namespace spence::extract {

struct YouTubeFormat {
    int itag = 0;
    std::string url;
    std::string mime_type;
    uint32_t bitrate = 0;
    uint32_t sample_rate = 0;
    uint8_t channels = 0;
};

bool is_youtube_url(const std::string& url);
std::string extract_video_id(const std::string& url);

}
