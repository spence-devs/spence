"""Exception types for spence"""


class SpenceError(Exception):
    """Base exception for all spence errors"""
    pass


class ResolverError(SpenceError):
    """Failed to resolve track"""
    pass


class UnsupportedPlatform(ResolverError):
    """Platform not supported"""
    pass


class TrackNotFound(ResolverError):
    """Track does not exist or is unavailable"""
    pass


class PlayerError(SpenceError):
    """Playback error"""
    pass


class InvalidState(PlayerError):
    """Operation invalid in current player state"""
    pass


class DecodeError(PlayerError):
    """Audio decode failed"""
    pass
