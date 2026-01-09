#include "spence/audio/filter.h"
#include <cmath>
#include <algorithm>

namespace spence::audio {

VolumeFilter::VolumeFilter(float volume) : volume_(volume) {}

void VolumeFilter::process(AudioFrame& frame) {
    frame.apply_volume(volume_);
}

void VolumeFilter::reset() {}

void VolumeFilter::set_volume(float volume) {
    volume_ = std::clamp(volume, 0.0f, 2.0f);
}

// Simplified EQ using biquad filters
class EqualizerFilter::Impl {
public:
    struct BiquadCoeffs {
        float b0, b1, b2, a1, a2;
        float z1 = 0.0f, z2 = 0.0f;
    };
    
    std::vector<BiquadCoeffs> coeffs;
    
    void add_band(float frequency, float gain, float bandwidth, uint32_t sample_rate) {
        BiquadCoeffs c;
        
        float omega = 2.0f * M_PI * frequency / sample_rate;
        float sn = std::sin(omega);
        float cs = std::cos(omega);
        float alpha = sn * std::sinh(std::log(2.0f) / 2.0f * bandwidth * omega / sn);
        float A = std::pow(10.0f, gain / 40.0f);
        
        c.b0 = 1.0f + alpha * A;
        c.b1 = -2.0f * cs;
        c.b2 = 1.0f - alpha * A;
        c.a1 = -2.0f * cs;
        c.a2 = 1.0f - alpha / A;
        
        float a0 = 1.0f + alpha / A;
        c.b0 /= a0;
        c.b1 /= a0;
        c.b2 /= a0;
        c.a1 /= a0;
        c.a2 /= a0;
        
        coeffs.push_back(c);
    }
    
    float process_sample(float sample) {
        for (auto& c : coeffs) {
            float out = c.b0 * sample + c.z1;
            c.z1 = c.b1 * sample - c.a1 * out + c.z2;
            c.z2 = c.b2 * sample - c.a2 * out;
            sample = out;
        }
        return sample;
    }
};

EqualizerFilter::EqualizerFilter(const std::vector<EqualizerBand>& bands, uint32_t sample_rate)
    : impl_(std::make_unique<Impl>()) {
    for (const auto& band : bands) {
        impl_->add_band(band.frequency, band.gain, band.bandwidth, sample_rate);
    }
}

void EqualizerFilter::process(AudioFrame& frame) {
    for (auto& sample : frame.samples) {
        sample = impl_->process_sample(sample);
    }
}

void EqualizerFilter::reset() {
    for (auto& c : impl_->coeffs) {
        c.z1 = 0.0f;
        c.z2 = 0.0f;
    }
}

// Simplified timescale using pitch shift
class TimescaleFilter::Impl {
public:
    float speed;
    float pitch;
    
    Impl(float s, float p) : speed(s), pitch(p) {}
};

TimescaleFilter::TimescaleFilter(float speed, float pitch, float rate, uint32_t sample_rate)
    : impl_(std::make_unique<Impl>(speed, pitch)) {}

void TimescaleFilter::process(AudioFrame& frame) {
    // Basic pitch shift via resampling
    if (impl_->pitch != 1.0f) {
        size_t new_size = static_cast<size_t>(frame.samples.size() / impl_->pitch);
        std::vector<float> resampled(new_size);
        
        for (size_t i = 0; i < new_size; ++i) {
            float pos = i * impl_->pitch;
            size_t idx = static_cast<size_t>(pos);
            
            if (idx + 1 < frame.samples.size()) {
                float frac = pos - idx;
                resampled[i] = frame.samples[idx] * (1.0f - frac) + 
                               frame.samples[idx + 1] * frac;
            }
        }
        
        frame.samples = std::move(resampled);
    }
}

void TimescaleFilter::reset() {}

TremoloFilter::TremoloFilter(float frequency, float depth, uint32_t sample_rate)
    : frequency_(frequency), depth_(depth), sample_rate_(sample_rate) {}

void TremoloFilter::process(AudioFrame& frame) {
    for (auto& sample : frame.samples) {
        float phase = 2.0f * M_PI * frequency_ * sample_index_ / sample_rate_;
        float modulator = 1.0f - depth_ * (1.0f - std::cos(phase)) / 2.0f;
        sample *= modulator;
        sample_index_++;
    }
}

void TremoloFilter::reset() {
    sample_index_ = 0;
}

// Vibrato using delay line modulation
class VibratoFilter::Impl {
public:
    float frequency;
    float depth;
    uint32_t sample_rate;
    std::vector<float> delay_line;
    size_t write_pos = 0;
    uint64_t sample_index = 0;
    
    Impl(float f, float d, uint32_t sr)
        : frequency(f), depth(d), sample_rate(sr) {
        delay_line.resize(static_cast<size_t>(sr * 0.02f));  // 20ms delay line
    }
};

VibratoFilter::VibratoFilter(float frequency, float depth, uint32_t sample_rate)
    : impl_(std::make_unique<Impl>(frequency, depth, sample_rate)) {}

void VibratoFilter::process(AudioFrame& frame) {
    for (auto& sample : frame.samples) {
        float phase = 2.0f * M_PI * impl_->frequency * impl_->sample_index / impl_->sample_rate;
        float delay_samples = impl_->depth * impl_->delay_line.size() * 0.5f * (1.0f + std::sin(phase));
        
        impl_->delay_line[impl_->write_pos] = sample;
        
        float read_pos = impl_->write_pos - delay_samples;
        if (read_pos < 0) read_pos += impl_->delay_line.size();
        
        size_t idx = static_cast<size_t>(read_pos);
        sample = impl_->delay_line[idx % impl_->delay_line.size()];
        
        impl_->write_pos = (impl_->write_pos + 1) % impl_->delay_line.size();
        impl_->sample_index++;
    }
}

void VibratoFilter::reset() {
    std::fill(impl_->delay_line.begin(), impl_->delay_line.end(), 0.0f);
    impl_->write_pos = 0;
    impl_->sample_index = 0;
}

FilterChain::FilterChain() = default;

void FilterChain::set_config(const FilterConfig& config, uint32_t sample_rate) {
    filters_.clear();
    
    // Volume always first
    if (config.volume != 1.0f) {
        filters_.push_back(std::make_unique<VolumeFilter>(config.volume));
    }
    
    // Equalizer
    if (!config.equalizer.empty()) {
        filters_.push_back(std::make_unique<EqualizerFilter>(config.equalizer, sample_rate));
    }
    
    // Timescale
    if (config.speed != 1.0f || config.pitch != 1.0f) {
        filters_.push_back(std::make_unique<TimescaleFilter>(
            config.speed, config.pitch, config.rate, sample_rate
        ));
    }
    
    // Tremolo
    if (config.tremolo_enabled) {
        filters_.push_back(std::make_unique<TremoloFilter>(
            config.tremolo_frequency, config.tremolo_depth, sample_rate
        ));
    }
    
    // Vibrato
    if (config.vibrato_enabled) {
        filters_.push_back(std::make_unique<VibratoFilter>(
            config.vibrato_frequency, config.vibrato_depth, sample_rate
        ));
    }
}

void FilterChain::process(AudioFrame& frame) {
    for (auto& filter : filters_) {
        filter->process(frame);
    }
}

void FilterChain::reset() {
    for (auto& filter : filters_) {
        filter->reset();
    }
}

}
