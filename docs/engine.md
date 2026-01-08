# Audio Engine

The native engine processes audio with deterministic timing and bounded resource usage.

## Frame Clock

**Virtual monotonic clock:**

```
timestamp = frame_index * frame_duration
frame_duration = 20ms (Discord requirement)
```

**Properties:**

- Never depends on wall-clock for scheduling
- Replay produces identical timestamps
- Drift correction via hard clamping

**Clock advancement:**

```cpp
void advance() {
    frame_index++;
    timestamp_us = frame_index * 20000;
}
```

## Audio Pipeline

```
Source → Decoder → Resampler → Encoder → RTP Packetizer
```

### Decoder

Extracts PCM samples from source format.

**Supported formats:**

- Opus (via libopus)
- Ogg/Opus
- WebM/Opus

**Output:**

48kHz stereo PCM, 20ms frames (1920 samples).

### Resampler

Converts arbitrary sample rates to 48kHz.

**Implementation:**

libsamplerate with SRC_SINC_BEST_QUALITY.

**Why always resample:**

Even if source is 48kHz, resampler ensures exact frame boundaries.

### Encoder

Produces Opus packets for Discord.

**Settings:**

- 48kHz stereo
- 20ms frame size
- Bitrate: 128kbps (configurable)
- VBR enabled
- FEC enabled (forward error correction)

**Output:**

Raw Opus packet, typically 200-400 bytes.

### RTP Packetizer

Wraps Opus in RTP for Discord.

**Header:**

```
[V=2][P][X][CC][M][PT=78][Sequence][Timestamp][SSRC]
```

**Sequence numbers:**

Monotonically increasing, wraps at 65535.

**Timestamps:**

Based on frame clock, increments by 960 per frame (48kHz * 0.02s).

## Player State Machine

```
IDLE → LOADING → READY → PLAYING → PAUSED → STOPPED
```

**State transitions:**

- `load()`: IDLE → LOADING → READY
- `play()`: READY → PLAYING
- `pause()`: PLAYING → PAUSED
- `stop()`: * → STOPPED

**Frame generation:**

Only in PLAYING state.

## Memory Management

**Buffer sizing:**

- Decode buffer: 10 frames (200ms)
- Resample buffer: 5 frames (100ms)
- Encode buffer: 5 frames (100ms)
- Output queue: 50 packets (1 second)

**Allocation strategy:**

Pre-allocate buffers at player creation, no runtime allocation during playback.

## Thread Pool

**Work-stealing scheduler:**

- Fixed number of worker threads (default 4)
- Lock-free task queue per worker
- Steal from other workers when idle

**Task model:**

Each player submits one task per frame:

```cpp
Task {
    player_id,
    frame_index,
    execute: decode → resample → encode
}
```

**Priority:**

FIFO within same player, no cross-player priority.

## Jitter Buffer

**Purpose:**

Absorb timing variance between frame generation and network transmission.

**Size:**

50ms (2.5 frames).

**Behavior:**

- Underrun: Insert silence (PLC)
- Overrun: Drop oldest packet

## Packet Loss Concealment

**Strategy:**

When frame missing, synthesize audio based on previous frame.

**Implementation:**

Opus native PLC via `opus_decode()` with NULL input.

**Quality:**

Effective for <5% packet loss, degrades gracefully beyond that.

## Determinism Details

**Deterministic:**

- Frame index sequence
- PCM sample values (given identical source)
- Opus encoding (with fixed seed)
- RTP sequence numbers

**Non-deterministic:**

- Actual wall-clock timing of frame generation
- Thread scheduling order
- Network transmission timing

**Replay verification:**

```python
# Generate checksum of audio frames
checksum1 = hash(player.play_to_end())

# Replay same track
player.seek(0)
checksum2 = hash(player.play_to_end())

assert checksum1 == checksum2
```

## Performance Characteristics

**CPU usage:**

~0.5% per active player on modern CPU (2023+ hardware).

**Memory:**

~2MB per player (buffers + state).

**Latency:**

40ms total (decode + resample + encode), well within Discord tolerance.

**Scalability:**

Linear up to thread pool saturation, graceful degradation beyond.

## Error Recovery

**Decode errors:**

Insert silence for failed frame, continue playback.

**Buffer underrun:**

Activate PLC, log warning, continue.

**Catastrophic failure:**

Stop player, report error to Python, clean up resources.

## Monitoring

**Metrics exposed to Python:**

- Frames generated
- Frames dropped
- Decode errors
- Buffer underruns
- CPU time per frame

**Health check:**

Player considered healthy if:
- Frame generation rate ≥ 95% of expected
- Error rate < 1%
- Memory usage stable
