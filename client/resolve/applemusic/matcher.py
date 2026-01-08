from client.api.track import Track
from client.resolve.youtube.search import search_youtube
from client.resolve.common.http import HTTPClient
from client.errors import TrackNotFound


def match_to_youtube(apple_data: dict, http: HTTPClient) -> Track:
    """Match Apple Music track to YouTube"""
    
    title = apple_data.get('title', '')
    artist = apple_data.get('artist', '')
    duration_ms = apple_data.get('duration_ms', 0)
    isrc = apple_data.get('isrc')
    
    query = f"{artist} {title}"
    if isrc:
        query = f"{query} {isrc}"
    
    results = search_youtube(query, limit=5, http=http)
    
    if not results:
        raise TrackNotFound(f"No YouTube match for: {query}")
    
    # Simple duration based matching
    best_match = min(
        results,
        key=lambda t: abs(t.duration - duration_ms)
    )
    
    best_match.platform = "applemusic"
    best_match.isrc = isrc
    
    return best_match
