#include "spence/audio/encoder.h"
#include <opus/opus.h>

namespace spence::audio {

class OpusEncoder::Impl {
public:
    ::OpusEncoder* encoder = nullptr;
    
    ~Impl() {
        if (encoder) {
            opus_encoder_destroy(encoder);
        }
    }
};

OpusEncoder::OpusEncoder(const Config& config)
    : impl_(std::make_unique<Impl>())
    , config_(config) {
    
    int error = 0;
    impl_->encoder = opus_encoder_create(
        config_.sample_rate,
        config_.channels,
        OPUS_APPLICATION_AUDIO,
        &error
    );
    
    if (error == OPUS_OK && impl_->encoder) {
        opus_encoder_ctl(impl_->encoder, OPUS_SET_BITRATE(config_.bitrate));
        opus_encoder_ctl(impl_->encoder, OPUS_SET_VBR(config_.vbr ? 1 : 0));
        opus_encoder_ctl(impl_->encoder, OPUS_SET_INBAND_FEC(config_.fec ? 1 : 0));
        opus_encoder_ctl(impl_->encoder, OPUS_SET_PACKET_LOSS_PERC(5));
    }
}

OpusEncoder::~OpusEncoder() = default;

bool OpusEncoder::encode_frame(const AudioFrame& frame, std::vector<uint8_t>& output) {
    if (!impl_->encoder) return false;
    
    // Max Opus packet size
    output.resize(4000);
    
    int bytes = opus_encode_float(
        impl_->encoder,
        frame.samples.data(),
        config_.frame_size,
        output.data(),
        output.size()
    );
    
    if (bytes < 0) {
        return false;
    }
    
    output.resize(bytes);
    return true;
}

}
