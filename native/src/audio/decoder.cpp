#include "spence/audio/decoder.h"
#include "spence/stream/opusstream.h"
#include <opus/opus.h>
#include <cstring>

namespace spence::audio {

class OpusDecoder::Impl {
public:
    ::OpusDecoder* decoder = nullptr;
    std::unique_ptr<stream::OpusStream> stream;
    uint64_t current_timestamp_ms = 0;
    
    ~Impl() {
        if (decoder) {
            opus_decoder_destroy(decoder);
        }
    }
};

OpusDecoder::OpusDecoder() : impl_(std::make_unique<Impl>()) {}

OpusDecoder::~OpusDecoder() {
    close();
}

bool OpusDecoder::open(const std::string& url) {
    impl_->stream = stream::create_opus_stream(url);
    if (!impl_->stream || !impl_->stream->open(url)) {
        return false;
    }
    
    int error = 0;
    impl_->decoder = opus_decoder_create(sample_rate_, channels_, &error);
    if (error != OPUS_OK) {
        return false;
    }
    
    duration_ms_ = impl_->stream->duration_ms();
    return true;
}

bool OpusDecoder::decode_frame(AudioFrame& frame) {
    if (!impl_->decoder || !impl_->stream) {
        return false;
    }
    
    stream::OpusPacket packet;
    if (!impl_->stream->read_packet(packet)) {
        return false;
    }
    
    frame.resize(960);  // 20ms at 48kHz
    frame.sample_rate = sample_rate_;
    frame.channels = channels_;
    
    int samples = opus_decode_float(
        impl_->decoder,
        packet.data.data(),
        packet.data.size(),
        frame.samples.data(),
        960,
        0  // no FEC
    );
    
    if (samples < 0) {
        // PLC: decode with null to synthesize missing frame
        samples = opus_decode_float(
            impl_->decoder,
            nullptr,
            0,
            frame.samples.data(),
            960,
            0
        );
        if (samples < 0) {
            return false;
        }
    }
    
    impl_->current_timestamp_ms = packet.timestamp_ms;
    return true;
}

bool OpusDecoder::seek(uint64_t timestamp_ms) {
    if (!impl_->stream) return false;
    
    bool success = impl_->stream->seek(timestamp_ms);
    if (success) {
        impl_->current_timestamp_ms = timestamp_ms;
        // Reset decoder state
        if (impl_->decoder) {
            opus_decoder_ctl(impl_->decoder, OPUS_RESET_STATE);
        }
    }
    return success;
}

void OpusDecoder::close() {
    if (impl_->stream) {
        impl_->stream->close();
        impl_->stream.reset();
    }
    if (impl_->decoder) {
        opus_decoder_destroy(impl_->decoder);
        impl_->decoder = nullptr;
    }
}

std::unique_ptr<Decoder> create_decoder(const std::string& url) {
    // Currently only Opus supported, expand later if needed
    return std::make_unique<OpusDecoder>();
}

}
