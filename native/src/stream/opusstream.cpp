#include "spence/stream/opusstream.h"
#include "spence/extract/webm.h"
#include <fstream>
#include <cstring>

namespace spence::stream {

class WebMOpusStream::Impl {
public:
    extract::WebMDemuxer demuxer;
    extract::WebMHeader header;
    bool opened = false;
    uint64_t current_timestamp_ns = 0;
};

WebMOpusStream::WebMOpusStream() : impl_(std::make_unique<Impl>()) {}

WebMOpusStream::~WebMOpusStream() {
    close();
}

bool WebMOpusStream::open(const std::string& url) {
    if (!impl_->demuxer.open(url)) {
        return false;
    }
    
    if (!impl_->demuxer.read_header(impl_->header)) {
        impl_->demuxer.close();
        return false;
    }
    
    impl_->opened = true;
    return true;
}

bool WebMOpusStream::read_packet(OpusPacket& packet) {
    if (!impl_->opened) return false;
    
    uint64_t timestamp_ns = 0;
    if (!impl_->demuxer.read_packet(packet.data, timestamp_ns)) {
        return false;
    }
    
    packet.timestamp_ms = timestamp_ns / 1000000;
    packet.duration_ms = 20;  // Opus frames are always 20ms
    
    impl_->current_timestamp_ns = timestamp_ns;
    return true;
}

bool WebMOpusStream::seek(uint64_t timestamp_ms) {
    if (!impl_->opened) return false;
    
    uint64_t timestamp_ns = timestamp_ms * 1000000;
    bool success = impl_->demuxer.seek(timestamp_ns);
    if (success) {
        impl_->current_timestamp_ns = timestamp_ns;
    }
    return success;
}

void WebMOpusStream::close() {
    if (impl_->opened) {
        impl_->demuxer.close();
        impl_->opened = false;
    }
}

uint64_t WebMOpusStream::duration_ms() const {
    return impl_->header.duration_ns / 1000000;
}

bool WebMOpusStream::is_open() const {
    return impl_->opened;
}

std::unique_ptr<OpusStream> create_opus_stream(const std::string& url) {
    // Detect format from URL or file extension
    if (url.find(".webm") != std::string::npos || url.find("mime=webm") != std::string::npos) {
        return std::make_unique<WebMOpusStream>();
    }
    
    // Default to WebM for YouTube URLs
    return std::make_unique<WebMOpusStream>();
}

}
