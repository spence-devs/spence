from client.api.track import Track
from client.resolve.youtube.search import search_youtube
from client.resolve.common.http import HTTPClient
from client.errors import TrackNotFound


def match_to_youtube(spotify_data: dict, http: HTTPClient) -> Track:
    """Match Spotify track to YouTube"""
    
    # Extract metadata
    title = spotify_data.get('name', '')
    artists = spotify_data.get('artists', [])
    artist = artists[0].get('name', '') if artists else ''
    duration_ms = spotify_data.get('duration_ms', 0)
    isrc = spotify_data.get('external_ids', {}).get('isrc')
    
    # Build search query
    query = f"{artist} {title}"
    if isrc:
        query = f"{query} {isrc}"
    
    # Search YouTube
    results = search_youtube(query, limit=5, http=http)
    
    if not results:
        raise TrackNotFound(f"No YouTube match for: {query}")
    
    # Find best match based on duration similarity
    best_match = _find_best_match(results, duration_ms, title, artist)
    
    if not best_match:
        raise TrackNotFound(f"No suitable YouTube match for: {query}")
    
    # Update metadata to reflect Spotify origin
    best_match.platform = "spotify"
    best_match.isrc = isrc
    
    return best_match


def _find_best_match(
    results: list[Track],
    target_duration: int,
    target_title: str,
    target_artist: str
) -> Track:
    """Find best matching track by duration and title similarity"""
    
    def score_match(track: Track) -> float:
        # Duration similarity (within 10 seconds is acceptable)
        duration_diff = abs(track.duration - target_duration)
        duration_score = max(0, 1.0 - (duration_diff / 10000.0))
        
        # Title similarity (basic string matching)
        title_lower = track.title.lower()
        target_lower = target_title.lower()
        title_score = 1.0 if target_lower in title_lower else 0.5
        
        # Artist similarity
        artist_lower = track.artist.lower()
        target_artist_lower = target_artist.lower()
        artist_score = 1.0 if target_artist_lower in artist_lower else 0.5
        
        return duration_score * 0.4 + title_score * 0.4 + artist_score * 0.2
    
    # Score all results
    scored = [(track, score_match(track)) for track in results]
    scored.sort(key=lambda x: x[1], reverse=True)
    
    # Return best if confidence >= 0.85
    if scored and scored[0][1] >= 0.85:
        return scored[0][0]
    
    # Fallback to first result
    return results[0] if results else None
