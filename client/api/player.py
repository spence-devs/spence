from typing import Optional
from dataclasses import dataclass
from client.api.track import Track
from client.api.filters import FilterConfig
from client.bridge.core import NativePlayer, NativeTrackInfo, PlayerState
from client.errors import InvalidState


@dataclass
class PlayerMetrics:
    """Playback metrics"""
    frames_generated: int
    frames_dropped: int
    decode_errors: int
    buffer_underruns: int
    avg_frame_time_us: float


class Player:
    """Controls playback of audio tracks"""
    
    def __init__(self, native: NativePlayer):
        self._native = native
        self._current_track: Optional[Track] = None
    
    def load(self, track: Track) -> None:
        """Load track into player"""
        info = NativeTrackInfo()
        info.stream_url = track.stream_url
        info.duration_ms = track.duration
        info.sample_rate = 48000
        info.channels = 2
        
        if not self._native.load(info):
            raise InvalidState("Failed to load track")
        
        self._current_track = track
    
    def play(self) -> None:
        """Start playback"""
        if not self._native.play():
            raise InvalidState("Cannot play in current state")
    
    def pause(self) -> None:
        """Pause playback"""
        if not self._native.pause():
            raise InvalidState("Cannot pause in current state")
    
    def stop(self) -> None:
        """Stop and reset"""
        if not self._native.stop():
            raise InvalidState("Cannot stop in current state")
        self._current_track = None
    
    def seek(self, position_ms: int) -> None:
        """Seek to position"""
        if not self._native.seek(position_ms):
            raise InvalidState("Cannot seek in current state")
    
    def set_volume(self, volume: float) -> None:
        """Set volume (0.0 to 2.0)"""
        self._native.set_volume(max(0.0, min(2.0, volume)))
    
    def read_frame(self) -> Optional[bytes]:
        """Read next 20ms Opus frame"""
        frame = self._native.read_frame()
        return frame if frame else None
    
    @property
    def position_ms(self) -> int:
        """Current playback position"""
        return self._native.position_ms
    
    @property
    def is_playing(self) -> bool:
        """Whether player is currently playing"""
        return self._native.state == PlayerState.PLAYING
    
    @property
    def is_paused(self) -> bool:
        """Whether player is paused"""
        return self._native.state == PlayerState.PAUSED
    
    @property
    def current_track(self) -> Optional[Track]:
        """Currently loaded track"""
        return self._current_track
    
    def metrics(self) -> PlayerMetrics:
        """Get playback metrics"""
        m = self._native.metrics()
        return PlayerMetrics(
            frames_generated=m.frames_generated,
            frames_dropped=m.frames_dropped,
            decode_errors=m.decode_errors,
            buffer_underruns=m.buffer_underruns,
            avg_frame_time_us=m.avg_frame_time_us,
        )
