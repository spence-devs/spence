import re
from client.resolve.base import Resolver
from client.api.track import Track
from client.resolve.deezer.matcher import match_to_youtube
from client.resolve.common.http import HTTPClient
from client.errors import TrackNotFound
import orjson


class DeezerResolver(Resolver):
    """Deezer metadata → YouTube resolution"""
    
    def __init__(self):
        self._http = HTTPClient()
    
    def can_resolve(self, query: str) -> bool:
        return 'deezer.com' in query
    
    def resolve(self, query: str) -> Track:
        track_id = self._extract_track_id(query)
        if not track_id:
            raise TrackNotFound(f"Invalid Deezer URL: {query}")
        
        metadata = self._fetch_metadata(track_id)
        if not metadata:
            raise TrackNotFound(f"Deezer track not found: {track_id}")
        
        return match_to_youtube(metadata, self._http)
    
    def search(self, query: str, limit: int = 10) -> list[Track]:
        results = self._search_deezer(query, limit)
        tracks = []
        
        for result in results:
            try:
                track = match_to_youtube(result, self._http)
                tracks.append(track)
            except Exception:
                continue
        
        return tracks
    
    @property
    def platform_name(self) -> str:
        return "deezer"
    
    def _extract_track_id(self, url: str) -> str:
        match = re.search(r'track/(\d+)', url)
        return match.group(1) if match else ""
    
    def _fetch_metadata(self, track_id: str) -> dict:
        """Fetch track metadata from Deezer API"""
        api_url = f"https://api.deezer.com/track/{track_id}"
        
        try:
            response = self._http.get(api_url)
            return orjson.loads(response)
        except Exception:
            return {}
    
    def _search_deezer(self, query: str, limit: int) -> list[dict]:
        """Search Deezer"""
        api_url = f"https://api.deezer.com/search?q={query}&limit={limit}"
        
        try:
            response = self._http.get(api_url)
            data = orjson.loads(response)
            return data.get('data', [])
        except Exception:
            return []
