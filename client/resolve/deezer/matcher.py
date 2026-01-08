from client.api.track import Track
from client.resolve.youtube.search import search_youtube
from client.resolve.common.http import HTTPClient
from client.errors import TrackNotFound


def match_to_youtube(deezer_data: dict, http: HTTPClient) -> Track:
    """Match Deezer track to YouTube"""
    
    title = deezer_data.get('title', '')
    artist = deezer_data.get('artist', {}).get('name', '')
    duration_ms = deezer_data.get('duration', 0) * 1000
    isrc = deezer_data.get('isrc')
    
    query = f"{artist} {title}"
    if isrc:
        query = f"{query} {isrc}"
    
    results = search_youtube(query, limit=5, http=http)
    
    if not results:
        raise TrackNotFound(f"No YouTube match for: {query}")
    
    best_match = min(
        results,
        key=lambda t: abs(t.duration - duration_ms)
    )
    
    best_match.platform = "deezer"
    best_match.isrc = isrc
    
    return best_match
