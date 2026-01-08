from dataclasses import dataclass
from typing import Optional


@dataclass
class Track:
    """Playable audio track"""
    
    id: str
    title: str
    artist: str
    duration: int  # milliseconds
    stream_url: str
    platform: str
    artwork_url: Optional[str] = None
    isrc: Optional[str] = None
    
    @property
    def duration_seconds(self) -> float:
        """Duration in seconds"""
        return self.duration / 1000.0
    
    def __str__(self) -> str:
        return f"{self.artist} - {self.title}"
    
    def __repr__(self) -> str:
        return f"Track(id={self.id!r}, title={self.title!r}, artist={self.artist!r})"
