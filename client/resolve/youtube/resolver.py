import re
from typing import Optional
from client.resolve.base import Resolver
from client.api.track import Track
from client.resolve.youtube.signature import decrypt_signature
from client.resolve.youtube.formats import select_opus_format
from client.resolve.youtube.search import search_youtube
from client.resolve.common.http import HTTPClient
from client.errors import TrackNotFound
import orjson


class YouTubeResolver(Resolver):
    """Direct YouTube audio resolution"""
    
    def __init__(self):
        self._http = HTTPClient()
    
    def can_resolve(self, query: str) -> bool:
        return bool(re.search(r'(youtube\.com|youtu\.be)', query))
    
    def resolve(self, query: str) -> Track:
        video_id = self._extract_video_id(query)
        if not video_id:
            raise TrackNotFound(f"Invalid YouTube URL: {query}")
        
        return self._resolve_video(video_id)
    
    def search(self, query: str, limit: int = 10) -> list[Track]:
        return search_youtube(query, limit, self._http)
    
    @property
    def platform_name(self) -> str:
        return "youtube"
    
    def _extract_video_id(self, url: str) -> Optional[str]:
        patterns = [
            r'youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})',
            r'youtu\.be/([a-zA-Z0-9_-]{11})',
            r'youtube\.com/embed/([a-zA-Z0-9_-]{11})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    def _resolve_video(self, video_id: str) -> Track:
        # Fetch video info
        url = f"https://www.youtube.com/watch?v={video_id}"
        html = self._http.get(url)
        
        # Extract ytInitialPlayerResponse
        match = re.search(r'ytInitialPlayerResponse\s*=\s*({.+?});', html)
        if not match:
            raise TrackNotFound("Failed to extract player response")
        
        data = orjson.loads(match.group(1))
        
        # Extract metadata
        details = data.get('videoDetails', {})
        title = details.get('title', 'Unknown')
        artist = details.get('author', 'Unknown')
        duration = int(details.get('lengthSeconds', 0)) * 1000
        
        # Select best Opus format
        formats = data.get('streamingData', {}).get('adaptiveFormats', [])
        opus_format = select_opus_format(formats)
        
        if not opus_format:
            raise TrackNotFound("No Opus stream available")
        
        stream_url = opus_format.get('url')
        
        # Decrypt signature if needed
        if not stream_url and 'signatureCipher' in opus_format:
            stream_url = decrypt_signature(
                opus_format['signatureCipher'],
                video_id,
                self._http
            )
        
        if not stream_url:
            raise TrackNotFound("Failed to resolve stream URL")
        
        return Track(
            id=video_id,
            title=title,
            artist=artist,
            duration=duration,
            stream_url=stream_url,
            platform="youtube",
            artwork_url=f"https://i.ytimg.com/vi/{video_id}/maxresdefault.jpg",
      )
