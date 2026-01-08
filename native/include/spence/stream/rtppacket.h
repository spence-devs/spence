#pragma once

#include <cstdint>
#include <vector>
#include <array>

namespace spence::stream {

class RTPPacket {
public:
    RTPPacket();
    
    void set_payload(const uint8_t* data, size_t len);
    void set_sequence(uint16_t seq);
    void set_timestamp(uint32_t ts);
    void set_ssrc(uint32_t ssrc);
    
    const std::vector<uint8_t>& data() const { return packet_; }
    size_t size() const { return packet_.size(); }
    
    uint16_t sequence() const { return sequence_; }
    uint32_t timestamp() const { return timestamp_; }
    
    void advance_sequence() { sequence_++; }
    void advance_timestamp(uint32_t delta) { timestamp_ += delta; }
    
private:
    void rebuild_header();
    
    std::vector<uint8_t> packet_;
    uint16_t sequence_ = 0;
    uint32_t timestamp_ = 0;
    uint32_t ssrc_ = 0;
    
    static constexpr uint8_t RTP_VERSION = 2;
    static constexpr uint8_t PAYLOAD_TYPE = 0x78;
    static constexpr size_t HEADER_SIZE = 12;
};

}
