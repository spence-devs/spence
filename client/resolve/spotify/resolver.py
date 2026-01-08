import re
from client.resolve.base import Resolver
from client.api.track import Track
from client.resolve.spotify.matcher import match_to_youtube
from client.resolve.spotify.auth import SpotifyAuth
from client.resolve.common.http import HTTPClient
from client.errors import TrackNotFound
import orjson


class SpotifyResolver(Resolver):
    """Spotify metadata → YouTube resolution"""
    
    def __init__(self):
        self._http = HTTPClient()
        self._auth = SpotifyAuth(self._http)
    
    def can_resolve(self, query: str) -> bool:
        return 'spotify.com' in query
    
    def resolve(self, query: str) -> Track:
        track_id = self._extract_track_id(query)
        if not track_id:
            raise TrackNotFound(f"Invalid Spotify URL: {query}")
        
        metadata = self._fetch_metadata(track_id)
        if not metadata:
            raise TrackNotFound(f"Spotify track not found: {track_id}")
        
        return match_to_youtube(metadata, self._http)
    
    def search(self, query: str, limit: int = 10) -> list[Track]:
        results = self._search_spotify(query, limit)
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
        return "spotify"
    
    def _extract_track_id(self, url: str) -> str:
        match = re.search(r'track/([a-zA-Z0-9]+)', url)
        return match.group(1) if match else ""
    
    def _fetch_metadata(self, track_id: str) -> dict:
        """Fetch track metadata from Spotify API"""
        token = self._auth.get_token()
        if not token:
            return {}
        
        api_url = f"https://api.spotify.com/v1/tracks/{track_id}"
        headers = {"Authorization": f"Bearer {token}"}
        
        try:
            response = self._http.get(api_url, headers=headers)
            return orjson.loads(response)
        except Exception:
            return {}
    
    def _search_spotify(self, query: str, limit: int) -> list[dict]:
        """Search Spotify"""
        token = self._auth.get_token()
        if not token:
            return []
        
        api_url = f"https://api.spotify.com/v1/search?q={query}&type=track&limit={limit}"
        headers = {"Authorization": f"Bearer {token}"}
        
        try:
            response = self._http.get(api_url, headers=headers)
            data = orjson.loads(response)
            return data.get('tracks', {}).get('items', [])
        except Exception:
            return []
