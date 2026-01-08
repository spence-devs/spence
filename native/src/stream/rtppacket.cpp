#include "spence/stream/rtppacket.h"
#include <cstring>

namespace spence::stream {

RTPPacket::RTPPacket() {
    packet_.resize(HEADER_SIZE);
}

void RTPPacket::set_payload(const uint8_t* data, size_t len) {
    packet_.resize(HEADER_SIZE + len);
    std::memcpy(packet_.data() + HEADER_SIZE, data, len);
    rebuild_header();
}

void RTPPacket::set_sequence(uint16_t seq) {
    sequence_ = seq;
    rebuild_header();
}

void RTPPacket::set_timestamp(uint32_t ts) {
    timestamp_ = ts;
    rebuild_header();
}

void RTPPacket::set_ssrc(uint32_t ssrc) {
    ssrc_ = ssrc;
    rebuild_header();
}

void RTPPacket::rebuild_header() {
    if (packet_.size() < HEADER_SIZE) return;
    
    // RTP v2 header: [V=2|P|X|CC|M|PT|Seq|Timestamp|SSRC]
    uint8_t* h = packet_.data();
    
    h[0] = (RTP_VERSION << 6);  // V=2, P=0, X=0, CC=0
    h[1] = PAYLOAD_TYPE;         // M=0, PT=0x78 (Discord Opus)
    
    // Sequence number (big endian)
    h[2] = (sequence_ >> 8) & 0xFF;
    h[3] = sequence_ & 0xFF;
    
    // Timestamp (big endian)
    h[4] = (timestamp_ >> 24) & 0xFF;
    h[5] = (timestamp_ >> 16) & 0xFF;
    h[6] = (timestamp_ >> 8) & 0xFF;
    h[7] = timestamp_ & 0xFF;
    
    // SSRC (big endian)
    h[8] = (ssrc_ >> 24) & 0xFF;
    h[9] = (ssrc_ >> 16) & 0xFF;
    h[10] = (ssrc_ >> 8) & 0xFF;
    h[11] = ssrc_ & 0xFF;
}

}
