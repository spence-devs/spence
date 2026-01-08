#pragma once

#include "spence/track.h"
#include "spence/audio/decoder.h"
#include "spence/audio/encoder.h"
#include "spence/audio/resampler.h"
#include "spence/stream/ringbuffer.h"
#include <cstdint>
#include <memory>
#include <atomic>
#include <mutex>
#include <vector>

namespace spence {

class Engine;

enum class PlayerState : uint8_t {
    Idle = 0,
    Loading = 1,
    Ready = 2,
    Playing = 3,
    Paused = 4,
    Stopped = 5,
};

struct PlayerMetrics {
    uint64_t frames_generated = 0;
    uint64_t frames_dropped = 0;
    uint32_t decode_errors = 0;
    uint32_t buffer_underruns = 0;
    uint64_t avg_frame_time_us = 0;
};

class Player : public std::enable_shared_from_this<Player> {
public:
    Player(Engine* engine, uint64_t id);
    ~Player();
    
    bool load(const TrackInfo& track);
    bool play();
    bool pause();
    bool stop();
    bool seek(uint64_t position_ms);
    void set_volume(float volume);
    
    bool read_frame(uint8_t* buffer, size_t buffer_size, size_t& bytes_written);
    
    uint64_t position_ms() const;
    PlayerState state() const;
    PlayerMetrics metrics() const;
    
    uint64_t id() const { return id_; }
    
private:
    void process_frame();
    void advance_clock();
    void schedule_next_frame();
    
    Engine* engine_;
    uint64_t id_;
    
    std::atomic<PlayerState> state_{PlayerState::Idle};
    std::atomic<uint64_t> frame_index_{0};
    std::atomic<float> volume_{1.0f};
    
    TrackInfo track_info_;
    std::unique_ptr<audio::Decoder> decoder_;
    std::unique_ptr<audio::Resampler> resampler_;
    std::unique_ptr<audio::Encoder> encoder_;
    
    RingBuffer<std::vector<uint8_t>> output_buffer_;
    
    mutable std::mutex metrics_mutex_;
    PlayerMetrics metrics_;
    
    static constexpr uint32_t SAMPLE_RATE = 48000;
    static constexpr uint32_t CHANNELS = 2;
    static constexpr uint32_t FRAME_SIZE = 960;
    static constexpr uint32_t FRAME_DURATION_MS = 20;
};

}
