import re
from client.resolve.base import Resolver
from client.api.track import Track
from client.resolve.applemusic.matcher import match_to_youtube
from client.resolve.common.http import HTTPClient
from client.errors import TrackNotFound
import orjson


class AppleMusicResolver(Resolver):
    """Apple Music metadata → YouTube resolution"""
    
    def __init__(self):
        self._http = HTTPClient()
    
    def can_resolve(self, query: str) -> bool:
        return 'music.apple.com' in query
    
    def resolve(self, query: str) -> Track:
        metadata = self._fetch_metadata(query)
        if not metadata:
            raise TrackNotFound(f"Apple Music track not found: {query}")
        
        return match_to_youtube(metadata, self._http)
    
    def search(self, query: str, limit: int = 10) -> list[Track]:
        # Apple Music search requires API key
        # Return empty for now
        return []
    
    @property
    def platform_name(self) -> str:
        return "applemusic"
    
    def _fetch_metadata(self, url: str) -> dict:
        """Extract metadata from Apple Music page"""
        try:
            html = self._http.get(url)
            
            # Extract structured data
            match = re.search(r'<script type="application/ld\+json">(.+?)</script>', html, re.DOTALL)
            if match:
                data = orjson.loads(match.group(1))
                
                # Parse MusicRecording schema
                if data.get('@type') == 'MusicRecording':
                    return {
                        'title': data.get('name', ''),
                        'artist': data.get('byArtist', {}).get('name', ''),
                        'duration_ms': self._parse_duration(data.get('duration', '')),
                        'isrc': data.get('isrcCode'),
                    }
        except Exception:
            pass
        
        return {}
    
    def _parse_duration(self, iso_duration: str) -> int:
        """Parse ISO 8601 duration to milliseconds"""
        # PT3M45S → 225000ms
        match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', iso_duration)
        if not match:
            return 0
        
        hours = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)
        seconds = int(match.group(3) or 0)
        
        return (hours * 3600 + minutes * 60 + seconds) * 1000
