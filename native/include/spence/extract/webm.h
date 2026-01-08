#pragma once

#include <cstdint>
#include <vector>
#include <string>
#include <memory>

namespace spence::extract {

struct WebMHeader {
    uint32_t sample_rate = 48000;
    uint8_t channels = 2;
    uint64_t duration_ns = 0;
    std::string codec;
};

class WebMDemuxer {
public:
    WebMDemuxer();
    ~WebMDemuxer();
    
    bool open(const std::string& path);
    bool read_header(WebMHeader& header);
    bool read_packet(std::vector<uint8_t>& data, uint64_t& timestamp_ns);
    bool seek(uint64_t timestamp_ns);
    void close();
    
    bool is_open() const;
    
private:
    class Impl;
    std::unique_ptr<Impl> impl_;
};

}
