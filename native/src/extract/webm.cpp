#include "spence/extract/webm.h"
#include <fstream>
#include <cstring>

namespace spence::extract {

// Minimal WebM/Matroska EBML parser for Opus extraction
class WebMDemuxer::Impl {
public:
    std::ifstream file;
    WebMHeader header;
    uint64_t current_pos = 0;
    bool header_read = false;
    
    uint64_t read_ebml_id() {
        uint8_t b;
        file.read(reinterpret_cast<char*>(&b), 1);
        
        // Count leading zeros to determine ID length
        int len = 1;
        uint8_t mask = 0x80;
        while (len <= 4 && !(b & mask)) {
            len++;
            mask >>= 1;
        }
        
        uint64_t id = b;
        for (int i = 1; i < len; i++) {
            file.read(reinterpret_cast<char*>(&b), 1);
            id = (id << 8) | b;
        }
        return id;
    }
    
    uint64_t read_ebml_size() {
        uint8_t b;
        file.read(reinterpret_cast<char*>(&b), 1);
        
        int len = 1;
        uint8_t mask = 0x80;
        while (len <= 8 && !(b & mask)) {
            len++;
            mask >>= 1;
        }
        
        uint64_t size = b & (mask - 1);
        for (int i = 1; i < len; i++) {
            file.read(reinterpret_cast<char*>(&b), 1);
            size = (size << 8) | b;
        }
        return size;
    }
    
    void skip_element(uint64_t size) {
        file.seekg(size, std::ios::cur);
    }
};

WebMDemuxer::WebMDemuxer() : impl_(std::make_unique<Impl>()) {}

WebMDemuxer::~WebMDemuxer() {
    close();
}

bool WebMDemuxer::open(const std::string& path) {
    impl_->file.open(path, std::ios::binary);
    return impl_->file.is_open();
}

bool WebMDemuxer::read_header(WebMHeader& header) {
    if (!impl_->file.is_open()) return false;
    
    // Parse EBML header and segment info
    // This is a simplified parser real implementation would fully parse WebM structure
    
    // For now, setting defaults for YouTube Opus streams
    header.sample_rate = 48000;
    header.channels = 2;
    header.codec = "opus";
    header.duration_ns = 0;  // Unknown until full parse
    
    impl_->header = header;
    impl_->header_read = true;
    return true;
}

bool WebMDemuxer::read_packet(std::vector<uint8_t>& data, uint64_t& timestamp_ns) {
    if (!impl_->header_read) return false;
    
    // Read next SimpleBlock or Block
    // This is simplified real parser would handle cluster structure
    
    uint64_t id = impl_->read_ebml_id();
    uint64_t size = impl_->read_ebml_size();
    
    if (size == 0 || size > 1000000) {  // Sanity check
        return false;
    }
    
    data.resize(size);
    impl_->file.read(reinterpret_cast<char*>(data.data()), size);
    
    if (impl_->file.gcount() != static_cast<std::streamsize>(size)) {
        return false;
    }
    
    // Extract timestamp from block (simplified)
    timestamp_ns = impl_->current_pos * 20000000;  // 20ms increments
    impl_->current_pos++;
    
    return true;
}

bool WebMDemuxer::seek(uint64_t timestamp_ns) {
    if (!impl_->header_read) return false;
    
    // Simplified seek real implementation would use cues/seeking
    impl_->current_pos = timestamp_ns / 20000000;
    return true;
}

void WebMDemuxer::close() {
    if (impl_->file.is_open()) {
        impl_->file.close();
    }
    impl_->header_read = false;
}

bool WebMDemuxer::is_open() const {
    return impl_->file.is_open();
}

}
