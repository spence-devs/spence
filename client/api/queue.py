from typing import Optional
from collections import deque
import random
from client.api.track import Track
from client.api.player import Player


class Queue:
    """Manages playlist of tracks"""
    
    def __init__(self, player: Player):
        self._player = player
        self._tracks: deque[Track] = deque()
        self._current: Optional[Track] = None
    
    def add(self, track: Track) -> None:
        """Add track to end of queue"""
        self._tracks.append(track)
    
    def add_next(self, track: Track) -> None:
        """Add track to play next"""
        self._tracks.appendleft(track)
    
    def remove(self, index: int) -> Track:
        """Remove and return track at index"""
        if index < 0 or index >= len(self._tracks):
            raise IndexError("Queue index out of range")
        
        track = self._tracks[index]
        del self._tracks[index]
        return track
    
    def clear(self) -> None:
        """Clear all tracks"""
        self._tracks.clear()
    
    def shuffle(self) -> None:
        """Shuffle remaining tracks"""
        tracks_list = list(self._tracks)
        random.shuffle(tracks_list)
        self._tracks = deque(tracks_list)
    
    def skip(self) -> Optional[Track]:
        """Skip to next track"""
        if not self._tracks:
            return None
        
        next_track = self._tracks.popleft()
        self._player.load(next_track)
        self._player.play()
        self._current = next_track
        return next_track
    
    @property
    def current(self) -> Optional[Track]:
        """Currently playing track"""
        return self._current
    
    @property
    def upcoming(self) -> list[Track]:
        """Remaining tracks in queue"""
        return list(self._tracks)
    
    @property
    def is_empty(self) -> bool:
        """Whether queue is empty"""
        return len(self._tracks) == 0
    
    def __len__(self) -> int:
        return len(self._tracks)
    
    def __iter__(self):
        return iter(self._tracks)
