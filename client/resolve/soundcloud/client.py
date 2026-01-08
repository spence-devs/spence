import re
from typing import Optional
from client.resolve.common.http import HTTPClient
import orjson


class SoundCloudClient:
    """SoundCloud API wrapper"""
    
    def __init__(self):
        self._http = HTTPClient()
        self._client_id: Optional[str] = None
    
    def resolve_url(self, url: str) -> Optional[dict]:
        """Resolve SoundCloud URL to track data"""
        client_id = self._get_client_id()
        if not client_id:
            return None
        
        api_url = f"https://api-v2.soundcloud.com/resolve?url={url}&client_id={client_id}"
        
        try:
            response = self._http.get(api_url)
            return orjson.loads(response)
        except Exception:
            return None
    
    def search(self, query: str, limit: int = 10) -> list[dict]:
        """Search SoundCloud"""
        client_id = self._get_client_id()
        if not client_id:
            return []
        
        api_url = (
            f"https://api-v2.soundcloud.com/search/tracks?"
            f"q={query}&client_id={client_id}&limit={limit}"
        )
        
        try:
            response = self._http.get(api_url)
            data = orjson.loads(response)
            return data.get('collection', [])
        except Exception:
            return []
    
    def get_stream_url(self, track_data: dict) -> str:
        """Get progressive stream URL"""
        # Try media.transcodings for progressive stream
        transcodings = track_data.get('media', {}).get('transcodings', [])
        
        for t in transcodings:
            if t.get('format', {}).get('protocol') == 'progressive':
                stream_url = t.get('url')
                if stream_url:
                    client_id = self._get_client_id()
                    return f"{stream_url}?client_id={client_id}"
        
        # Fallback to legacy stream_url
        return track_data.get('stream_url', '')
    
    def _get_client_id(self) -> Optional[str]:
        """Extract client ID from SoundCloud app"""
        if self._client_id:
            return self._client_id
        
        try:
            html = self._http.get("https://soundcloud.com")
            
            # Find script URLs
            script_urls = re.findall(r'<script[^>]+src="([^"]+)"', html)
            
            for script_url in script_urls:
                if 'app' in script_url:
                    js = self._http.get(script_url)
                    
                    # Extract client_id
                    match = re.search(r'client_id:"([a-zA-Z0-9]+)"', js)
                    if match:
                        self._client_id = match.group(1)
                        return self._client_id
        except Exception:
            pass
        
        return None
