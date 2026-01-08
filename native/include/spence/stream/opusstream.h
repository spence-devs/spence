#pragma once

#include <string>
#include <vector>
#include <cstdint>
#include <memory>

namespace spence::stream {

struct OpusPacket {
    std::vector<uint8_t> data;
    uint64_t timestamp_ms = 0;
    uint64_t duration_ms = 0;
};

class OpusStream {
public:
    virtual ~OpusStream() = default;
    
    virtual bool open(const std::string& url) = 0;
    virtual bool read_packet(OpusPacket& packet) = 0;
    virtual bool seek(uint64_t timestamp_ms) = 0;
    virtual void close() = 0;
    
    virtual uint64_t duration_ms() const = 0;
    virtual bool is_open() const = 0;
};

class WebMOpusStream : public OpusStream {
public:
    WebMOpusStream();
    ~WebMOpusStream() override;
    
    bool open(const std::string& url) override;
    bool read_packet(OpusPacket& packet) override;
    bool seek(uint64_t timestamp_ms) override;
    void close() override;
    
    uint64_t duration_ms() const override;
    bool is_open() const override;
    
private:
    class Impl;
    std::unique_ptr<Impl> impl_;
};

std::unique_ptr<OpusStream> create_opus_stream(const std::string& url);

}
