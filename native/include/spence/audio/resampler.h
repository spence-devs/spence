#pragma once

#include "spence/audio/frame.h"
#include <memory>
#include <cstdint>

namespace spence::audio {

class Resampler {
public:
    virtual ~Resampler() = default;
    
    virtual bool resample(const AudioFrame& input, AudioFrame& output) = 0;
    virtual void reset() = 0;
};

class LibsamplerateResampler : public Resampler {
public:
    LibsamplerateResampler(
        uint32_t input_rate,
        uint32_t output_rate,
        uint8_t channels
    );
    ~LibsamplerateResampler() override;
    
    bool resample(const AudioFrame& input, AudioFrame& output) override;
    void reset() override;
    
private:
    class Impl;
    std::unique_ptr<Impl> impl_;
    
    uint32_t input_rate_;
    uint32_t output_rate_;
    uint8_t channels_;
    double ratio_;
};

}
