import re
from urllib.parse import quote_plus
from client.api.track import Track
from client.resolve.common.http import HTTPClient
import orjson


def search_youtube(query: str, limit: int, http: HTTPClient) -> list[Track]:
    """Search YouTube for tracks"""
    
    url = f"https://www.youtube.com/results?search_query={quote_plus(query)}"
    html = http.get(url)
    
    # Extract ytInitialData
    match = re.search(r'ytInitialData\s*=\s*({.+?});', html)
    if not match:
        return []
    
    data = orjson.loads(match.group(1))
    
    # Navigate to video results
    contents = data.get('contents', {})
    results_data = contents.get('twoColumnSearchResultsRenderer', {})
    primary = results_data.get('primaryContents', {})
    section = primary.get('sectionListRenderer', {})
    contents_list = section.get('contents', [])
    
    tracks = []
    
    for content in contents_list:
        items = content.get('itemSectionRenderer', {}).get('contents', [])
        
        for item in items:
            video = item.get('videoRenderer')
            if not video:
                continue
            
            video_id = video.get('videoId')
            if not video_id:
                continue
            
            title_runs = video.get('title', {}).get('runs', [])
            title = title_runs[0].get('text', 'Unknown') if title_runs else 'Unknown'
            
            owner_runs = video.get('ownerText', {}).get('runs', [])
            artist = owner_runs[0].get('text', 'Unknown') if owner_runs else 'Unknown'
            
            length_text = video.get('lengthText', {}).get('simpleText', '0:00')
            duration = _parse_duration(length_text)
            
            track = Track(
                id=video_id,
                title=title,
                artist=artist,
                duration=duration,
                stream_url=f"https://www.youtube.com/watch?v={video_id}",
                platform="youtube",
                artwork_url=f"https://i.ytimg.com/vi/{video_id}/maxresdefault.jpg",
            )
            
            tracks.append(track)
            
            if len(tracks) >= limit:
                break
        
        if len(tracks) >= limit:
            break
    
    return tracks[:limit]


def _parse_duration(text: str) -> int:
    """Parse duration string like '3:45' to milliseconds"""
    parts = text.split(':')
    
    if len(parts) == 2:
        minutes, seconds = int(parts[0]), int(parts[1])
        return (minutes * 60 + seconds) * 1000
    elif len(parts) == 3:
        hours, minutes, seconds = int(parts[0]), int(parts[1]), int(parts[2])
        return (hours * 3600 + minutes * 60 + seconds) * 1000
    
    return 0
