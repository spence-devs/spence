from typing import Optional


def select_opus_format(formats: list[dict]) -> Optional[dict]:
    """Select best Opus format from adaptive formats"""
    
    # Prefer format 251 (Opus 160kbps)
    for fmt in formats:
        if fmt.get('itag') == 251:
            return fmt
    
    # Fallback to format 250 (Opus 70kbps)
    for fmt in formats:
        if fmt.get('itag') == 250:
            return fmt
    
    # Any Opus format
    for fmt in formats:
        mime = fmt.get('mimeType', '')
        if 'opus' in mime.lower():
            return fmt
    
    return None


def get_format_quality(fmt: dict) -> int:
    """Get quality score for format"""
    itag = fmt.get('itag', 0)
    
    quality_map = {
        251: 100,  # Opus 160kbps
        250: 80,   # Opus 70kbps
        249: 60,   # Opus 50kbps
    }
    
    return quality_map.get(itag, 0)
