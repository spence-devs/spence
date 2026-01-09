from client.__version__ import __version__
from client.api.node import Node
from client.api.player import Player
from client.api.track import Track
from client.api.queue import Queue
from client.api.filters import FilterConfig, EqualizerBand, Filters
from client.errors import (
    SpenceError,
    ResolverError,
    UnsupportedPlatform,
    TrackNotFound,
    PlayerError,
    InvalidState,
    DecodeError,
)

__all__ = [
    "__version__",
    "Node",
    "Player",
    "Track",
    "Queue",
    "FilterConfig",
    "EqualizerBand",
    "Filters",
    "SpenceError",
    "ResolverError",
    "UnsupportedPlatform",
    "TrackNotFound",
    "PlayerError",
    "InvalidState",
    "DecodeError",
]
