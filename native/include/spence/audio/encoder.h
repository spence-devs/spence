#pragma once

#include "spence/audio/frame.h"
#include <memory>
#include <cstdint>
#include <vector>

namespace spence::audio {

class Encoder {
public:
    virtual ~Encoder() = default;
    
    virtual bool encode_frame(const AudioFrame& frame, std::vector<uint8_t>& output) = 0;
};

class OpusEncoder : public Encoder {
public:
    struct Config {
        uint32_t sample_rate = 48000;
        uint8_t channels = 2;
        uint32_t bitrate = 128000;
        uint32_t frame_size = 960;
        bool vbr = true;
        bool fec = true;
    };
    
    explicit OpusEncoder(const Config& config = Config{});
    ~OpusEncoder() override;
    
    bool encode_frame(const AudioFrame& frame, std::vector<uint8_t>& output) override;
    
private:
    class Impl;
    std::unique_ptr<Impl> impl_;
    Config config_;
};

}
