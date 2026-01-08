# Resolver System

Resolvers translate platform URLs into playable TrackDescriptors.

## Resolver Types

### Direct Resolvers

Extract actual audio stream URLs.

**YouTube:**

- Targets format 251 (Opus in WebM)
- Native signature decryption
- Adaptive format fallback
- 6-hour URL expiration

**SoundCloud:**

- API-based resolution
- Progressive MP3/Opus streams
- Client ID rotation

### Metadata Resolvers

Match metadata to playable sources.

**Spotify, Apple Music, Deezer:**

1. Extract track metadata (title, artist, ISRC)
2. Search YouTube for best match
3. Return YouTube TrackDescriptor

**Why YouTube?**

Broadest catalog, reliable availability, Opus streams.

## Router Logic

```python
url → detect platform → select resolver → resolve → cache
```

**Platform detection:**

- URL pattern matching
- Domain-based routing
- Search query fallback

**Fallback chain:**

1. Primary resolver
2. Metadata match if available
3. Search query resolution
4. Failure

## Caching Strategy

**Cache key:** Platform + track ID

**TTL policy:**

- YouTube streams: 6 hours (URL expiration)
- Metadata matches: 24 hours
- Search results: 1 hour

**Eviction:**

LRU with hard size limit (default 10k entries).

## Resolver Interface

```python
class Resolver(ABC):
    @abstractmethod
    def can_resolve(self, query: str) -> bool:
        pass

    @abstractmethod
    def resolve(self, query: str) -> TrackDescriptor:
        pass

    @abstractmethod
    def search(self, query: str, limit: int) -> List[TrackDescriptor]:
        pass
```

## YouTube Resolver

**Signature decryption:**

YouTube obfuscates stream URLs with JavaScript-based signature functions. We extract and execute these functions in Python.

**Format selection:**

1. Prefer format 251 (Opus, 160kbps)
2. Fallback to 250 (Opus, 70kbps)
3. Fallback to adaptive DASH

**Rate limiting:**

- Per-IP throttling detection
- Exponential backoff on 429
- Distributed resolution for high volume

## SoundCloud Resolver

**Client ID extraction:**

SoundCloud uses rotating client IDs embedded in their web player. We extract these automatically.

**Stream types:**

- Progressive: Direct MP3/Opus URL
- HLS: M3U8 playlist (avoided)

## Metadata Matching

**ISRC-based matching:**

International Standard Recording Code provides exact track identification.

**Fuzzy matching fallback:**

1. Normalize title and artist
2. YouTube search
3. Score results by:
   - Title similarity
   - Artist match
   - Duration match
   - View count heuristic

**Match confidence threshold:**

Minimum 0.85 similarity score to avoid bad matches.

## Error Handling

**Transient errors:**

- Network timeouts: Retry with backoff
- Rate limits: Queue and delay
- Temporary unavailability: Mark and retry

**Permanent errors:**

- Deleted content: Fail immediately
- Geo-restrictions: Report to caller
- Invalid format: Fail fast

## Resolver Registry

Dynamic resolver registration:

```python
registry = ResolverRegistry()
registry.register(YouTubeResolver())
registry.register(SoundCloudResolver())
registry.register(SpotifyResolver())
```

Custom resolvers can be added at runtime.

## Performance

**Resolution latency:**

- YouTube: 200-500ms (with signature decrypt)
- SoundCloud: 100-300ms
- Metadata match: 300-800ms (includes search)

**Cache hit rate:**

Target 80%+ in production with warm cache.

**Concurrent resolution:**

Resolvers are thread-safe and support parallel requests.
