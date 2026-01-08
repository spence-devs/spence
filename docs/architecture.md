# Architecture

spence is designed around three core principles: determinism, scalability, and platform independence.

## System Layers

### Native Engine (C++)

The native engine handles all audio processing with zero Python involvement.

**Components:**

- **Frame Clock**: Virtual monotonic clock advancing by 20ms per frame
- **Audio Pipeline**: Decode → Resample → Encode with fixed-rate processing
- **Opus Codec**: Direct integration with libopus for Discord compatibility
- **WebM Demuxer**: Native extraction of Opus packets from YouTube streams
- **Thread Pool**: Bounded work-stealing scheduler for multi-guild concurrency

**Key characteristics:**

- Frame index is source of truth: `timestamp = frame_index * 20ms`
- No wall-clock dependency in scheduling logic
- Deterministic replay: same input → same output
- Bounded memory growth with hard queue limits

### Resolver System (Python)

Platform-specific track resolution with aggressive caching.

**Resolver types:**

1. **Direct resolvers**: YouTube, SoundCloud (audio URLs)
2. **Metadata resolvers**: Spotify, Apple Music, Deezer (match to YouTube)

**Flow:**

```
User URL → Router → Resolver → TrackDescriptor
                       ↓
                   Cache layer
                       ↓
              Native engine playback
```

**Caching strategy:**

- In-memory LRU with TTL enforcement
- YouTube URLs expire after 6 hours
- Metadata matches cached for 24 hours
- No unbounded growth

### Discord Integration (Python)

Optional layer for Discord voice connectivity.

- RTP packet construction in C++
- Sequence numbers and timestamps managed natively
- Python handles only WebSocket transport

## Threading Model

**Native side:**

- Bounded thread pool (default: 4 workers)
- Work-stealing for load balancing
- One task per player per frame
- GIL released during audio processing

**Python side:**

- asyncio for orchestration only
- No audio timing in Python
- Resolution requests are synchronous but non-blocking

## Memory Model

**Bounded queues everywhere:**

- Audio buffer: 5 seconds max
- Decode queue: 10 frames ahead
- Packet queue: 50 packets (1 second)

**Backpressure:**

When queues fill, producers block rather than allocate unbounded memory.

## Determinism Guarantees

**What is deterministic:**

- Frame generation order
- Audio sample values
- Packet sequence numbers
- RTP timestamps

**What is not deterministic:**

- Actual wall-clock timing (varies by system load)
- Network I/O patterns
- Resolver response times

**Replay safety:**

Given identical TrackDescriptor and start frame, playback produces identical audio.

## Scalability Design

**Target: 1000 concurrent guilds on 8-core VPS**

- Each player consumes ~2MB resident memory
- CPU scales linearly with active players
- Decode parallelism bounded by thread pool
- No per-guild threads

**Graceful degradation:**

- Under load, frame generation may lag wall-clock
- Discord sees this as minor jitter, not breakage
- System remains stable, never crashes

## Platform Independence

**No runtime dependencies:**

- No ffmpeg binary
- No Java runtime
- No external services

**Vendored libraries:**

- libopus (audio codec)
- libogg (container format)
- libsamplerate (resampling)

Static linking ensures reproducible builds across environments.
