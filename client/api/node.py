from typing import Optional
from client.bridge.core import NativeNode, NativeNodeConfig
from client.api.player import Player
from client.api.track import Track
from client.resolve.router import Router
from client.resolve.cache import ResolverCache


class Node:
    """Central orchestration for audio engine and resolvers"""
    
    def __init__(
        self,
        thread_pool_size: int = 4,
        cache_size: int = 10000,
        cache_ttl: int = 21600,
    ):
        """
        Args:
            thread_pool_size: Native worker threads
            cache_size: Max resolver cache entries
            cache_ttl: Cache TTL in seconds (default 6h)
        """
        config = NativeNodeConfig()
        config.thread_pool_size = thread_pool_size
        
        self._native = NativeNode(config)
        self._router = Router()
        self._cache = ResolverCache(max_size=cache_size, ttl=cache_ttl)
    
    def resolve(self, query: str) -> Track:
        """Resolve URL or search query to track"""
        cached = self._cache.get(query)
        if cached:
            return cached
        
        track = self._router.resolve(query)
        self._cache.set(query, track)
        return track
    
    def search(self, query: str, limit: int = 10) -> list[Track]:
        """Search for tracks"""
        return self._router.search(query, limit)
    
    def create_player(self) -> Player:
        """Create new player instance"""
        native_player = self._native.create_player()
        return Player(native_player)
    
    def shutdown(self) -> None:
        """Clean shutdown"""
        self._cache.clear()
