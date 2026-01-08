try:
    from client.bridge._native import (
        Node as NativeNode,
        NodeConfig as NativeNodeConfig,
        Player as NativePlayer,
        PlayerState,
        PlayerMetrics as NativeMetrics,
        TrackInfo as NativeTrackInfo,
    )
except ImportError as e:
    raise ImportError(
        "Native module not found. Build with: python tools/build.py"
    ) from e

__all__ = [
    "NativeNode",
    "NativeNodeConfig",
    "NativePlayer",
    "PlayerState",
    "NativeMetrics",
    "NativeTrackInfo",
]
