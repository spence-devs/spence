import re
from time import time
from typing import Optional
from client.resolve.common.http import HTTPClient
import orjson


class SpotifyAuth:
    """Manages Spotify API tokens"""
    
    def __init__(self, http: HTTPClient):
        self._http = http
        self._token: Optional[str] = None
        self._token_expires: float = 0
    
    def get_token(self) -> Optional[str]:
        """Get valid access token"""
        if self._token and time() < self._token_expires:
            return self._token
        
        self._refresh_token()
        return self._token
    
    def _refresh_token(self) -> None:
        """Obtain new client credentials token"""
        # Extract embedded token from Spotify web player
        # This avoids need for client_id/client_secret
        
        try:
            html = self._http.get("https://open.spotify.com")
            
            # Find embedded token in page
            match = re.search(r'accessToken":"([^"]+)"', html)
            if match:
                self._token = match.group(1)
                self._token_expires = time() + 3600
                return
        except Exception:
            pass
        
        self._token = None
        self._token_expires = 0
