# API Reference

## Node

Central orchestration point for audio engine and resolvers.

```python
class Node:
    def __init__(
        self,
        thread_pool_size: int = 4,
        cache_size: int = 10000,
        cache_ttl: int = 21600,
    ) -> None:
        """Initialize audio node.
        
        Args:
            thread_pool_size: Native worker threads
            cache_size: Max resolver cache entries
            cache_ttl: Cache TTL in seconds (default 6h)
        """
```

### Methods

```python
def resolve(self, query: str) -> Track:
    """Resolve URL or search query to track."""

def search(self, query: str, limit: int = 10) -> list[Track]:
    """Search for tracks."""

def create_player(self) -> Player:
    """Create new player instance."""

def shutdown(self) -> None:
    """Clean shutdown of node."""
```

## Track

Represents a playable audio track.

```python
@dataclass
class Track:
    id: str
    title: str
    artist: str
    duration: int  # milliseconds
    stream_url: str
    platform: str
    artwork_url: str | None = None
    isrc: str | None = None
```

### Properties

```python
@property
def duration_ms(self) -> int:
    """Duration in milliseconds."""

@property
def duration_seconds(self) -> float:
    """Duration in seconds."""
```

## Player

Controls playback of audio tracks.

```python
class Player:
    def load(self, track: Track) -> None:
        """Load track into player."""

    def play(self) -> None:
        """Start playback."""

    def pause(self) -> None:
        """Pause playback."""

    def stop(self) -> None:
        """Stop and reset."""

    def seek(self, position_ms: int) -> None:
        """Seek to position."""

    def set_volume(self, volume: float) -> None:
        """Set volume (0.0 to 2.0)."""

    def read_frame(self) -> bytes | None:
        """Read next 20ms Opus frame.
        
        Returns:
            Opus packet bytes, or None if no frame ready
        """

    @property
    def position_ms(self) -> int:
        """Current playback position."""

    @property
    def is_playing(self) -> bool:
        """Whether player is currently playing."""

    @property
    def is_paused(self) -> bool:
        """Whether player is paused."""
```

## Queue

Manages playlist of tracks.

```python
class Queue:
    def __init__(self, player: Player) -> None:
        """Create queue for player."""

    def add(self, track: Track) -> None:
        """Add track to end of queue."""

    def add_next(self, track: Track) -> None:
        """Add track to play next."""

    def remove(self, index: int) -> Track:
        """Remove and return track at index."""

    def clear(self) -> None:
        """Clear all tracks."""

    def shuffle(self) -> None:
        """Shuffle remaining tracks."""

    def skip(self) -> Track | None:
        """Skip to next track."""

    @property
    def current(self) -> Track | None:
        """Currently playing track."""

    @property
    def upcoming(self) -> list[Track]:
        """Remaining tracks in queue."""

    @property
    def is_empty(self) -> bool:
        """Whether queue is empty."""
```

## Discord Integration

### VoiceClient

Wrapper around discord.py voice client.

```python
class VoiceClient:
    def __init__(
        self,
        voice_client: discord.VoiceClient,
        player: Player,
    ) -> None:
        """Create voice client wrapper."""

    async def connect(self) -> None:
        """Start audio transmission."""

    async def disconnect(self) -> None:
        """Stop audio transmission."""

    @property
    def is_connected(self) -> bool:
        """Whether connected to voice."""
```

### Usage

```python
import discord
import spence

bot = discord.Bot()
node = spence.Node()

@bot.command()
async def play(ctx, query: str):
    voice = await ctx.author.voice.channel.connect()
    
    track = node.resolve(query)
    player = node.create_player()
    player.load(track)
    
    vc = spence.VoiceClient(voice, player)
    await vc.connect()
    player.play()
```

## Exceptions

```python
class SpenceError(Exception):
    """Base exception."""

class ResolverError(SpenceError):
    """Resolution failed."""

class UnsupportedPlatform(ResolverError):
    """Platform not supported."""

class TrackNotFound(ResolverError):
    """Track does not exist."""

class PlayerError(SpenceError):
    """Playback error."""

class InvalidState(PlayerError):
    """Invalid player state."""

class DecodeError(PlayerError):
    """Audio decode failed."""
```

## Configuration

### Environment Variables

```bash
SPENCE_THREAD_POOL_SIZE=4
SPENCE_CACHE_SIZE=10000
SPENCE_CACHE_TTL=21600
SPENCE_LOG_LEVEL=INFO
```

### Programmatic Config

```python
import spence

spence.set_log_level("DEBUG")
spence.enable_metrics()

node = spence.Node(
    thread_pool_size=8,
    cache_size=50000,
)
```

## Metrics

```python
@dataclass
class Metrics:
    frames_generated: int
    frames_dropped: int
    decode_errors: int
    buffer_underruns: int
    avg_frame_time_us: float
    cache_hits: int
    cache_misses: int

player.get_metrics() -> Metrics
```

## Type Hints

Full typing support with py.typed marker.

```python
from spence import Node, Player, Track, Queue
from typing import Optional, List

def create_playlist(node: Node, queries: List[str]) -> Queue:
    player = node.create_player()
    queue = Queue(player)
    
    for query in queries:
        track = node.resolve(query)
        queue.add(track)
    
    return queue
```
