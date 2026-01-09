#pragma once

#include "spence/audio/frame.h"
#include <vector>
#include <memory>
#include <cstdint>

namespace spence::audio {

struct EqualizerBand {
    float frequency;
    float gain;
    float bandwidth;
};

struct FilterConfig {
    float volume = 1.0f;
    
    std::vector<EqualizerBand> equalizer;
    
    bool karaoke_enabled = false;
    float karaoke_level = 1.0f;
    float karaoke_mono_level = 1.0f;
    float karaoke_filter_band = 220.0f;
    float karaoke_filter_width = 100.0f;
    
    float speed = 1.0f;
    float pitch = 1.0f;
    float rate = 1.0f;
    
    bool tremolo_enabled = false;
    float tremolo_frequency = 2.0f;
    float tremolo_depth = 0.5f;
    
    bool vibrato_enabled = false;
    float vibrato_frequency = 2.0f;
    float vibrato_depth = 0.5f;
    
    bool rotation_enabled = false;
    float rotation_speed = 0.0f;
    
    bool distortion_enabled = false;
    bool low_pass_enabled = false;
    float low_pass_smoothing = 20.0f;
};

class AudioFilter {
public:
    virtual ~AudioFilter() = default;
    virtual void process(AudioFrame& frame) = 0;
    virtual void reset() = 0;
};

class VolumeFilter : public AudioFilter {
public:
    explicit VolumeFilter(float volume);
    void process(AudioFrame& frame) override;
    void reset() override;
    void set_volume(float volume);
    
private:
    float volume_;
};

class EqualizerFilter : public AudioFilter {
public:
    explicit EqualizerFilter(const std::vector<EqualizerBand>& bands, uint32_t sample_rate);
    void process(AudioFrame& frame) override;
    void reset() override;
    
private:
    class Impl;
    std::unique_ptr<Impl> impl_;
};

class TimescaleFilter : public AudioFilter {
public:
    TimescaleFilter(float speed, float pitch, float rate, uint32_t sample_rate);
    void process(AudioFrame& frame) override;
    void reset() override;
    
private:
    class Impl;
    std::unique_ptr<Impl> impl_;
};

class TremoloFilter : public AudioFilter {
public:
    TremoloFilter(float frequency, float depth, uint32_t sample_rate);
    void process(AudioFrame& frame) override;
    void reset() override;
    
private:
    float frequency_;
    float depth_;
    uint32_t sample_rate_;
    uint64_t sample_index_ = 0;
};

class VibratoFilter : public AudioFilter {
public:
    VibratoFilter(float frequency, float depth, uint32_t sample_rate);
    void process(AudioFrame& frame) override;
    void reset() override;
    
private:
    class Impl;
    std::unique_ptr<Impl> impl_;
};

class FilterChain {
public:
    FilterChain();
    
    void set_config(const FilterConfig& config, uint32_t sample_rate);
    void process(AudioFrame& frame);
    void reset();
    
private:
    std::vector<std::unique_ptr<AudioFilter>> filters_;
};

}
