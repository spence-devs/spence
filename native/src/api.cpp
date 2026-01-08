#include "spence/api.h"
#include "spence/engine.h"
#include "spence/player.h"
#include <cstring>

struct SpenceEngine {
    spence::Engine engine;
    explicit SpenceEngine(uint32_t threads) : engine(threads) {}
};

struct SpencePlayer {
    std::shared_ptr<spence::Player> player;
    explicit SpencePlayer(std::shared_ptr<spence::Player> p) : player(std::move(p)) {}
};

extern "C" {

SpenceEngine* spence_engine_create(uint32_t thread_pool_size) {
    try {
        return new SpenceEngine(thread_pool_size);
    } catch (...) {
        return nullptr;
    }
}

void spence_engine_destroy(SpenceEngine* engine) {
    delete engine;
}

SpencePlayer* spence_engine_create_player(SpenceEngine* engine) {
    if (!engine) return nullptr;
    
    try {
        auto player = engine->engine.create_player();
        return new SpencePlayer(player);
    } catch (...) {
        return nullptr;
    }
}

SpenceStatus spence_player_load(SpencePlayer* player, const SpenceTrackInfo* info) {
    if (!player || !info) return SPENCE_ERR_INVALID_ARG;
    
    spence::TrackInfo track;
    track.stream_url = info->stream_url;
    track.duration_ms = info->duration_ms;
    track.sample_rate = info->sample_rate;
    track.channels = info->channels;
    
    return player->player->load(track) ? SPENCE_OK : SPENCE_ERR_DECODE_FAILED;
}

SpenceStatus spence_player_play(SpencePlayer* player) {
    if (!player) return SPENCE_ERR_INVALID_ARG;
    return player->player->play() ? SPENCE_OK : SPENCE_ERR_INVALID_STATE;
}

SpenceStatus spence_player_pause(SpencePlayer* player) {
    if (!player) return SPENCE_ERR_INVALID_ARG;
    return player->player->pause() ? SPENCE_OK : SPENCE_ERR_INVALID_STATE;
}

SpenceStatus spence_player_stop(SpencePlayer* player) {
    if (!player) return SPENCE_ERR_INVALID_ARG;
    return player->player->stop() ? SPENCE_OK : SPENCE_ERR_INVALID_STATE;
}

SpenceStatus spence_player_seek(SpencePlayer* player, uint64_t position_ms) {
    if (!player) return SPENCE_ERR_INVALID_ARG;
    return player->player->seek(position_ms) ? SPENCE_OK : SPENCE_ERR_INVALID_STATE;
}

SpenceStatus spence_player_set_volume(SpencePlayer* player, float volume) {
    if (!player) return SPENCE_ERR_INVALID_ARG;
    player->player->set_volume(volume);
    return SPENCE_OK;
}

SpenceStatus spence_player_read_frame(
    SpencePlayer* player,
    uint8_t* buffer,
    size_t buffer_size,
    size_t* bytes_written
) {
    if (!player || !buffer || !bytes_written) return SPENCE_ERR_INVALID_ARG;
    
    size_t written = 0;
    bool success = player->player->read_frame(buffer, buffer_size, written);
    *bytes_written = written;
    
    return success ? SPENCE_OK : SPENCE_ERR_INVALID_STATE;
}

uint64_t spence_player_get_position(SpencePlayer* player) {
    return player ? player->player->position_ms() : 0;
}

SpencePlayerState spence_player_get_state(SpencePlayer* player) {
    if (!player) return SPENCE_STATE_IDLE;
    return static_cast<SpencePlayerState>(player->player->state());
}

void spence_player_get_metrics(SpencePlayer* player, SpenceMetrics* metrics) {
    if (!player || !metrics) return;
    
    auto m = player->player->metrics();
    metrics->frames_generated = m.frames_generated;
    metrics->frames_dropped = m.frames_dropped;
    metrics->decode_errors = m.decode_errors;
    metrics->buffer_underruns = m.buffer_underruns;
    metrics->avg_frame_time_us = m.avg_frame_time_us;
}

void spence_player_destroy(SpencePlayer* player) {
    delete player;
}

}
