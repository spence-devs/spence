import re
from client.resolve.base import Resolver
from client.api.track import Track
from client.resolve.soundcloud.client import SoundCloudClient
from client.errors import TrackNotFound


class SoundCloudResolver(Resolver):
    """Direct SoundCloud resolution"""
    
    def __init__(self):
        self._client = SoundCloudClient()
    
    def can_resolve(self, query: str) -> bool:
        return 'soundcloud.com' in query
    
    def resolve(self, query: str) -> Track:
        data = self._client.resolve_url(query)
        if not data:
            raise TrackNotFound(f"SoundCloud track not found: {query}")
        
        return self._parse_track(data)
    
    def search(self, query: str, limit: int = 10) -> list[Track]:
        results = self._client.search(query, limit)
        return [self._parse_track(t) for t in results]
    
    @property
    def platform_name(self) -> str:
        return "soundcloud"
    
    def _parse_track(self, data: dict) -> Track:
        track_id = str(data.get('id', ''))
        title = data.get('title', 'Unknown')
        artist = data.get('user', {}).get('username', 'Unknown')
        duration = data.get('duration', 0)
        
        # Get progressive stream URL
        stream_url = self._client.get_stream_url(data)
        
        artwork = data.get('artwork_url')
        if artwork:
            artwork = artwork.replace('large', 't500x500')
        
        return Track(
            id=track_id,
            title=title,
            artist=artist,
            duration=duration,
            stream_url=stream_url,
            platform="soundcloud",
            artwork_url=artwork,
        )
