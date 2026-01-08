#include "spence/extract/youtube.h"
#include <regex>

namespace spence::extract {

bool is_youtube_url(const std::string& url) {
    return url.find("youtube.com") != std::string::npos ||
           url.find("youtu.be") != std::string::npos;
}

std::string extract_video_id(const std::string& url) {
    // Match youtube.com/watch?v=VIDEO_ID
    std::regex watch_regex(R"(youtube\.com/watch\?v=([a-zA-Z0-9_-]{11}))");
    std::smatch match;
    if (std::regex_search(url, match, watch_regex)) {
        return match[1].str();
    }
    
    // Match youtu.be/VIDEO_ID
    std::regex short_regex(R"(youtu\.be/([a-zA-Z0-9_-]{11}))");
    if (std::regex_search(url, match, short_regex)) {
        return match[1].str();
    }
    
    return "";
}

}
