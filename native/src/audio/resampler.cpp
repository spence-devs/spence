#include "spence/audio/resampler.h"
#include <samplerate.h>
#include <cstring>

namespace spence::audio {

class LibsamplerateResampler::Impl {
public:
    SRC_STATE* state = nullptr;
    
    ~Impl() {
        if (state) {
            src_delete(state);
        }
    }
};

LibsamplerateResampler::LibsamplerateResampler(
    uint32_t input_rate,
    uint32_t output_rate,
    uint8_t channels
)
    : impl_(std::make_unique<Impl>())
    , input_rate_(input_rate)
    , output_rate_(output_rate)
    , channels_(channels)
    , ratio_(static_cast<double>(output_rate) / input_rate) {
    
    int error = 0;
    impl_->state = src_new(SRC_SINC_BEST_QUALITY, channels, &error);
}

LibsamplerateResampler::~LibsamplerateResampler() = default;

bool LibsamplerateResampler::resample(const AudioFrame& input, AudioFrame& output) {
    if (!impl_->state) return false;
    
    SRC_DATA data;
    data.data_in = const_cast<float*>(input.samples.data());
    data.input_frames = input.num_samples();
    data.data_out = output.samples.data();
    data.output_frames = output.num_samples();
    data.src_ratio = ratio_;
    data.end_of_input = 0;
    
    int error = src_process(impl_->state, &data);
    if (error != 0) {
        return false;
    }
    
    output.samples.resize(data.output_frames_gen * channels_);
    return true;
}

void LibsamplerateResampler::reset() {
    if (impl_->state) {
        src_reset(impl_->state);
    }
}

}
