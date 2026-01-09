#include "spence/player.h"
#include "spence/engine.h"
#include <chrono>

namespace spence {

Player::Player(Engine* engine, uint64_t id)
    : engine_(engine)
    , id_(id)
    , output_buffer_(50)
    , filter_chain_(std::make_unique<audio::FilterChain>()) {
}

Player::~Player() {
    stop();
}

bool Player::load(const TrackInfo& track) {
    if (!track.is_valid()) return false;
    
    state_ = PlayerState::Loading;
    track_info_ = track;
    
    // Create decoder for stream
    decoder_ = audio::create_decoder(track.stream_url);
    if (!decoder_ || !decoder_->open(track.stream_url)) {
        state_ = PlayerState::Idle;
        return false;
    }
    
    // Setup resampler if needed
    if (decoder_->sample_rate() != SAMPLE_RATE) {
        resampler_ = std::make_unique<audio::LibsamplerateResampler>(
            decoder_->sample_rate(),
            SAMPLE_RATE,
            CHANNELS
        );
    }
    
    // Create encoder
    audio::OpusEncoder::Config enc_config;
    enc_config.sample_rate = SAMPLE_RATE;
    enc_config.channels = CHANNELS;
    enc_config.frame_size = FRAME_SIZE;
    encoder_ = std::make_unique<audio::OpusEncoder>(enc_config);
    
    frame_index_ = 0;
    state_ = PlayerState::Ready;
    return true;
}

bool Player::play() {
    PlayerState expected = PlayerState::Ready;
    if (!state_.compare_exchange_strong(expected, PlayerState::Playing)) {
        expected = PlayerState::Paused;
        if (!state_.compare_exchange_strong(expected, PlayerState::Playing)) {
            return false;
        }
    }
    
    schedule_next_frame();
    return true;
}

bool Player::pause() {
    PlayerState expected = PlayerState::Playing;
    return state_.compare_exchange_strong(expected, PlayerState::Paused);
}

bool Player::stop() {
    state_ = PlayerState::Stopped;
    output_buffer_.clear();
    frame_index_ = 0;
    return true;
}

bool Player::seek(uint64_t position_ms) {
    if (!decoder_) return false;
    
    bool was_playing = state_ == PlayerState::Playing;
    if (was_playing) pause();
    
    bool success = decoder_->seek(position_ms);
    if (success) {
        frame_index_ = position_ms / FRAME_DURATION_MS;
        output_buffer_.clear();
        if (resampler_) resampler_->reset();
    }
    
    if (was_playing) play();
    return success;
}

void Player::set_volume(float volume) {
    volume_ = std::clamp(volume, 0.0f, 2.0f);
}

void Player::set_filters(const audio::FilterConfig& config) {
    filter_chain_->set_config(config, SAMPLE_RATE);
}

bool Player::read_frame(uint8_t* buffer, size_t buffer_size, size_t& bytes_written) {
    auto packet = output_buffer_.try_pop();
    if (!packet) {
        bytes_written = 0;
        
        std::lock_guard lock(metrics_mutex_);
        metrics_.buffer_underruns++;
        return false;
    }
    
    size_t size = std::min(packet->size(), buffer_size);
    std::memcpy(buffer, packet->data(), size);
    bytes_written = size;
    
    return true;
}

uint64_t Player::position_ms() const {
    return frame_index_.load(std::memory_order_relaxed) * FRAME_DURATION_MS;
}

PlayerState Player::state() const {
    return state_.load(std::memory_order_relaxed);
}

PlayerMetrics Player::metrics() const {
    std::lock_guard lock(metrics_mutex_);
    return metrics_;
}

void Player::process_frame() {
    auto start = std::chrono::steady_clock::now();
    
    audio::AudioFrame pcm_frame(FRAME_SIZE, SAMPLE_RATE, CHANNELS);
    
    // Decode
    if (!decoder_->decode_frame(pcm_frame)) {
        std::lock_guard lock(metrics_mutex_);
        metrics_.decode_errors++;
        pcm_frame.fill_silence();
    }
    
    // Resample if needed
    audio::AudioFrame resampled_frame;
    if (resampler_) {
        resampled_frame.resize(FRAME_SIZE);
        resampled_frame.sample_rate = SAMPLE_RATE;
        resampled_frame.channels = CHANNELS;
        
        if (!resampler_->resample(pcm_frame, resampled_frame)) {
            resampled_frame = std::move(pcm_frame);
        }
    } else {
        resampled_frame = std::move(pcm_frame);
    }
    
    // Apply volume
    float vol = volume_.load(std::memory_order_relaxed);
    if (vol != 1.0f) {
        resampled_frame.apply_volume(vol);
    }
    
    // Apply filters
    filter_chain_->process(resampled_frame);
    
    // Encode
    std::vector<uint8_t> opus_packet;
    if (encoder_->encode_frame(resampled_frame, opus_packet)) {
        if (!output_buffer_.try_push(std::move(opus_packet))) {
            std::lock_guard lock(metrics_mutex_);
            metrics_.frames_dropped++;
        }
    } else {
        std::lock_guard lock(metrics_mutex_);
        metrics_.decode_errors++;
    }
    
    auto end = std::chrono::steady_clock::now();
    auto duration_us = std::chrono::duration_cast<std::chrono::microseconds>(end - start).count();
    
    {
        std::lock_guard lock(metrics_mutex_);
        metrics_.frames_generated++;
        // Rolling average
        metrics_.avg_frame_time_us = 
            (metrics_.avg_frame_time_us * 99 + duration_us) / 100;
    }
    
    advance_clock();
    schedule_next_frame();
}

void Player::advance_clock() {
    frame_index_.fetch_add(1, std::memory_order_relaxed);
}

void Player::schedule_next_frame() {
    if (state_.load(std::memory_order_relaxed) != PlayerState::Playing) {
        return;
    }
    
    auto self = shared_from_this();
    uint64_t next_frame = frame_index_.load(std::memory_order_relaxed);
    
    Task task{
        .player_id = id_,
        .frame_index = next_frame,
        .execute = [self]() { self->process_frame(); }
    };
    
    engine_->submit_task(std::move(task));
}

}
