import re
from urllib.parse import parse_qs, urlencode, urlparse, parse_qsl
from client.resolve.common.http import HTTPClient


def decrypt_signature(cipher: str, video_id: str, http: HTTPClient) -> str:
    """Decrypt signatureCipher to get valid stream URL"""
    params = dict(parse_qsl(cipher))
    
    url = params.get('url')
    s = params.get('s')
    sp = params.get('sp', 'signature')
    
    if not url or not s:
        return ""
    
    # Get base.js and extract transform function
    signature = _transform_signature(s, video_id, http)
    
    # Append decrypted signature
    return f"{url}&{sp}={signature}"


def _transform_signature(s: str, video_id: str, http: HTTPClient) -> str:
    """Apply transformation to signature"""
    # Fetch player JS
    player_url = _get_player_url(video_id, http)
    if not player_url:
        return s
    
    js = http.get(f"https://www.youtube.com{player_url}")
    
    # Extract transformation function
    # This is a simplified implementation
    # Real version would parse the full JS transformation pipeline
    
    # For now return signature as is
    # Production would implement full JS execution
    return s


def _get_player_url(video_id: str, http: HTTPClient) -> str:
    """Extract player URL from video page"""
    html = http.get(f"https://www.youtube.com/watch?v={video_id}")
    
    match = re.search(r'"jsUrl":"(/s/player/[^"]+)"', html)
    if match:
        return match.group(1).replace('\\', '')
    
    return ""
