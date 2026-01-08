from client.api.track import Track
from client.resolve.registry import ResolverRegistry
from client.resolve.youtube.resolver import YouTubeResolver
from client.resolve.soundcloud.resolver import SoundCloudResolver
from client.resolve.spotify.resolver import SpotifyResolver
from client.resolve.applemusic.resolver import AppleMusicResolver
from client.resolve.deezer.resolver import DeezerResolver
from client.errors import UnsupportedPlatform


class Router:
    """Routes queries to appropriate resolvers"""
    
    def __init__(self):
        self._registry = ResolverRegistry()
        
        # Register resolvers in priority order
        self._registry.register(YouTubeResolver())
        self._registry.register(SoundCloudResolver())
        self._registry.register(SpotifyResolver())
        self._registry.register(AppleMusicResolver())
        self._registry.register(DeezerResolver())
    
    def resolve(self, query: str) -> Track:
        """Resolve URL or search query"""
        resolver = self._registry.get_resolver(query)
        if not resolver:
            # Fallback to YouTube search
            yt = self._registry.get_resolver("https://youtube.com")
            if yt:
                results = yt.search(query, limit=1)
                if results:
                    return results[0]
            raise UnsupportedPlatform(f"No resolver for: {query}")
        
        return resolver.resolve(query)
    
    def search(self, query: str, limit: int = 10) -> list[Track]:
        """Search across platforms"""
        # Use YouTube for search by default
        yt = self._registry.get_resolver("https://youtube.com")
        if yt:
            return yt.search(query, limit)
        return []
