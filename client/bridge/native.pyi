from enum import IntEnum
from typing import Optional


class PlayerState(IntEnum):
    IDLE: int
    LOADING: int
    READY: int
    PLAYING: int
    PAUSED: int
    STOPPED: int


class PlayerMetrics:
    frames_generated: int
    frames_dropped: int
    decode_errors: int
    buffer_underruns: int
    avg_frame_time_us: float


class TrackInfo:
    stream_url: str
    duration_ms: int
    sample_rate: int
    channels: int
    
    def is_valid(self) -> bool: ...


class Player:
    def load(self, info: TrackInfo) -> bool: ...
    def play(self) -> bool: ...
    def pause(self) -> bool: ...
    def stop(self) -> bool: ...
    def seek(self, position_ms: int) -> bool: ...
    def set_volume(self, volume: float) -> None: ...
    def read_frame(self) -> bytes: ...
    
    @property
    def position_ms(self) -> int: ...
    
    @property
    def state(self) -> PlayerState: ...
    
    def metrics(self) -> PlayerMetrics: ...


class NodeConfig:
    thread_pool_size: int


class Node:
    def __init__(self, config: NodeConfig = ...) -> None: ...
    def create_player(self) -> Player: ...
