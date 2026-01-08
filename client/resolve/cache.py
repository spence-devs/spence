from typing import Optional
from collections import OrderedDict
from time import time
from client.api.track import Track


class ResolverCache:
    """Thread-safe LRU cache with TTL"""
    
    def __init__(self, max_size: int = 10000, ttl: int = 21600):
        self._cache: OrderedDict[str, tuple[Track, float]] = OrderedDict()
        self._max_size = max_size
        self._ttl = ttl
    
    def get(self, key: str) -> Optional[Track]:
        """Get cached track if valid"""
        if key not in self._cache:
            return None
        
        track, timestamp = self._cache[key]
        
        # Check TTL
        if time() - timestamp > self._ttl:
            del self._cache[key]
            return None
        
        # Move to end (LRU)
        self._cache.move_to_end(key)
        return track
    
    def set(self, key: str, track: Track) -> None:
        """Cache track with current timestamp"""
        if key in self._cache:
            self._cache.move_to_end(key)
        
        self._cache[key] = (track, time())
        
        # Evict oldest if over capacity
        if len(self._cache) > self._max_size:
            self._cache.popitem(last=False)
    
    def clear(self) -> None:
        """Clear all cached entries"""
        self._cache.clear()
