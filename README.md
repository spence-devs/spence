<img align="right" src="https://i.postimg.cc/hvq26JFW/spence.png" width=200 alt="Spence">

# spence
A package that provides a deterministic, high-performance music infrastructure for Discord bots and streaming applications.

> Native audio engine for large-scale Discord music bots
> 

---

## EOL / Project Status

> This project is currently in **active development**.

> spence is designed as a long-term replacement for Java-based audio backends such as Lavalink, focusing on determinism, performance, and native execution.

> Breaking changes may occur until the first stable release.

---

## Features

- [x] Deterministic audio playback with frame-accurate timing  
- [x] Native C++ audio engine with Python bindings  
- [x] Multi-platform music resolution (YouTube, SoundCloud, Spotify, Apple Music, Deezer)  
- [x] Zero runtime ffmpeg dependency  
- [x] Opus-native pipeline with WebM demuxing  
- [x] Designed for large-scale sharded Discord bots  
- [x] Replay-safe and crash-resilient execution model  

---

## NOTE

> This library is **not** a drop-in Lavalink clone.  
> It is a low-level music infrastructure layer intended for engineers who need control, predictability, and scale.

> Audio processing **never runs in Python**. Python is only used for orchestration and integration.

> Discord voice transport and RTP handling are expected to be implemented by the consumer.

> This project prioritizes correctness and determinism over convenience.

---

## Requirements

- Python 3.11+
- CMake 3.20+
- C++20 compatible compiler  
  - GCC 12+
  - Clang 15+
  - MSVC 2022+
- Discord voice connection (for Discord bots)

---

## Installation

```bash
pip install spence
````

Build from source:

```bash
git clone https://github.com/spence-devs/spence.git
cd spence
python tools/build.py
pip install -e .
```

---

## Documentation

> [https://spence-devs.github.io/spence/](https://spence-devs.github.io/spence/)

---


## Example

> Running spence requires manual integration with your Discord voice system.
> Below is a minimal example demonstrating the core audio flow.

### Example usage

```python
import spence
import asyncio

node = spence.Node()

track = node.resolve("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

player = node.create_player()
player.load(track)
player.play()

while player.is_playing():
    frame = player.read_frame()  # 20ms Opus packet
    # send frame to Discord voice gateway
    await asyncio.sleep(0.02)
```

---

## Pro Tip

> spence exposes low-level playback state and timing data that can be used for:

* Metrics and monitoring
* Drift detection
* Playback validation
* Debugging voice desync issues

```python
player.on("frame_sent", lambda frame: ...)
player.on("track_end", lambda track: ...)
player.on("underrun", lambda state: ...)
```

> WARNING:
> DO NOT mutate or override internal engine state.
> The engine is designed to be driven, not modified.

---

## Platform Support

| Platform    | Resolution Strategy | Audio Source | Status |
| ----------- | ------------------- | ------------ | ------ |
| YouTube     | Direct              | Opus         | Stable |
| SoundCloud  | Direct              | MP3 / Opus   | Stable |
| Spotify     | Metadata → YouTube  | YouTube      | Stable |
| Apple Music | Metadata → YouTube  | YouTube      | Stable |
| Deezer      | Metadata → YouTube  | YouTube      | Stable |

---

## Versioning

> v0.1.0 — Active development
> v1.1.0 — First stable release (planned)

---

## License

MIT License

---

> Built for engineers who care about determinism, scale, and correctness.
