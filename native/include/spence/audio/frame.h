#pragma once

#include <vector>
#include <cstdint>
#include <cstring>

namespace spence::audio {

struct AudioFrame {
    std::vector<float> samples;
    uint32_t sample_rate = 48000;
    uint8_t channels = 2;
    
    AudioFrame() = default;
    
    AudioFrame(size_t num_samples, uint32_t rate, uint8_t ch)
        : samples(num_samples * ch), sample_rate(rate), channels(ch) {}
    
    void resize(size_t num_samples) {
        samples.resize(num_samples * channels);
    }
    
    void clear() {
        samples.clear();
    }
    
    void fill_silence() {
        std::memset(samples.data(), 0, samples.size() * sizeof(float));
    }
    
    size_t num_samples() const {
        return samples.size() / channels;
    }
    
    bool is_empty() const {
        return samples.empty();
    }
    
    void apply_volume(float volume) {
        for (auto& s : samples) {
            s *= volume;
        }
    }
};

}
