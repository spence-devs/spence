#pragma once

#include "spence/audio/frame.h"
#include <string>
#include <memory>
#include <cstdint>

namespace spence::audio {

class Decoder {
public:
    virtual ~Decoder() = default;
    
    virtual bool open(const std::string& url) = 0;
    virtual bool decode_frame(AudioFrame& frame) = 0;
    virtual bool seek(uint64_t timestamp_ms) = 0;
    virtual void close() = 0;
    
    virtual uint32_t sample_rate() const = 0;
    virtual uint8_t channels() const = 0;
    virtual uint64_t duration_ms() const = 0;
};

class OpusDecoder : public Decoder {
public:
    OpusDecoder();
    ~OpusDecoder() override;
    
    bool open(const std::string& url) override;
    bool decode_frame(AudioFrame& frame) override;
    bool seek(uint64_t timestamp_ms) override;
    void close() override;
    
    uint32_t sample_rate() const override { return sample_rate_; }
    uint8_t channels() const override { return channels_; }
    uint64_t duration_ms() const override { return duration_ms_; }
    
private:
    class Impl;
    std::unique_ptr<Impl> impl_;
    
    uint32_t sample_rate_ = 48000;
    uint8_t channels_ = 2;
    uint64_t duration_ms_ = 0;
};

std::unique_ptr<Decoder> create_decoder(const std::string& url);

}
