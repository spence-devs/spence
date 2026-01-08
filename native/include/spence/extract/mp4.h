#pragma once

#include <cstdint>
#include <vector>
#include <string>
#include <memory>

namespace spence::extract {

struct MP4Header {
    uint32_t sample_rate = 48000;
    uint8_t channels = 2;
    uint64_t duration_ms = 0;
    std::string codec;
};

class MP4Demuxer {
public:
    MP4Demuxer();
    ~MP4Demuxer();
    
    bool open(const std::string& path);
    bool read_header(MP4Header& header);
    bool read_packet(std::vector<uint8_t>& data, uint64_t& timestamp_ms);
    bool seek(uint64_t timestamp_ms);
    void close();
    
    bool is_open() const;
    
private:
    class Impl;
    std::unique_ptr<Impl> impl_;
};

}
