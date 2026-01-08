#pragma once

#include <cstdint>
#include <cstddef>

#if defined(_WIN32)
    #define SPENCE_API __declspec(dllexport)
#else
    #define SPENCE_API __attribute__((visibility("default")))
#endif

extern "C" {

typedef struct SpenceEngine SpenceEngine;
typedef struct SpencePlayer SpencePlayer;

typedef enum {
    SPENCE_OK = 0,
    SPENCE_ERR_INVALID_ARG = 1,
    SPENCE_ERR_OUT_OF_MEMORY = 2,
    SPENCE_ERR_INVALID_STATE = 3,
    SPENCE_ERR_DECODE_FAILED = 4,
    SPENCE_ERR_ENCODE_FAILED = 5,
} SpenceStatus;

typedef enum {
    SPENCE_STATE_IDLE = 0,
    SPENCE_STATE_LOADING = 1,
    SPENCE_STATE_READY = 2,
    SPENCE_STATE_PLAYING = 3,
    SPENCE_STATE_PAUSED = 4,
    SPENCE_STATE_STOPPED = 5,
} SpencePlayerState;

typedef struct {
    char stream_url[2048];
    uint64_t duration_ms;
    uint32_t sample_rate;
    uint8_t channels;
} SpenceTrackInfo;

typedef struct {
    uint64_t frames_generated;
    uint64_t frames_dropped;
    uint32_t decode_errors;
    uint32_t buffer_underruns;
    uint64_t avg_frame_time_us;
} SpenceMetrics;

SPENCE_API SpenceEngine* spence_engine_create(uint32_t thread_pool_size);
SPENCE_API void spence_engine_destroy(SpenceEngine* engine);
SPENCE_API SpencePlayer* spence_engine_create_player(SpenceEngine* engine);

SPENCE_API SpenceStatus spence_player_load(SpencePlayer* player, const SpenceTrackInfo* info);
SPENCE_API SpenceStatus spence_player_play(SpencePlayer* player);
SPENCE_API SpenceStatus spence_player_pause(SpencePlayer* player);
SPENCE_API SpenceStatus spence_player_stop(SpencePlayer* player);
SPENCE_API SpenceStatus spence_player_seek(SpencePlayer* player, uint64_t position_ms);
SPENCE_API SpenceStatus spence_player_set_volume(SpencePlayer* player, float volume);

SPENCE_API SpenceStatus spence_player_read_frame(
    SpencePlayer* player,
    uint8_t* buffer,
    size_t buffer_size,
    size_t* bytes_written
);

SPENCE_API uint64_t spence_player_get_position(SpencePlayer* player);
SPENCE_API SpencePlayerState spence_player_get_state(SpencePlayer* player);
SPENCE_API void spence_player_get_metrics(SpencePlayer* player, SpenceMetrics* metrics);
SPENCE_API void spence_player_destroy(SpencePlayer* player);

}
