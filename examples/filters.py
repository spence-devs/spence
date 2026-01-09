import spence
from spence import Filters
from spence.api.filters import FilterConfig, EqualizerBand
import time


def demo_presets(player: spence.Player):
    """Demo built in filter presets"""
    
    print("\nFilter Presets Demo\n")
    
    presets = [
        ("Nightcore", Filters.nightcore()),
        ("Vaporwave", Filters.vaporwave()),
        ("Bass Boost", Filters.bassboost(level=0.3)),
        ("Soft", Filters.soft()),
        ("Tremolo", Filters.tremolo()),
        ("8D Rotation", Filters.rotation()),
        ("Karaoke", Filters.karaoke()),
    ]
    
    for name, config in presets:
        print(f"Applying {name}...")
        player.set_filters(config)
        
        # Play for 3 seconds
        for _ in range(150):  # 3 seconds at 50fps
            frame = player.read_frame()
            time.sleep(0.02)
        
        print(f"  ✓ {name} applied\n")


def demo_custom_eq(player: spence.Player):
    """Demo custom equalizer"""
    
    print("\nCustom Equalizer Demo\n")
    
    # V-shaped EQ (boost bass and treble, cut mids)
    config = FilterConfig(
        equalizer=[
            EqualizerBand(25, 8.0, 1.0),    # Deep bass
            EqualizerBand(40, 6.0, 1.0),    # Bass
            EqualizerBand(160, 4.0, 1.0),   # Low mids
            EqualizerBand(400, -3.0, 1.0),  # Mids (cut)
            EqualizerBand(1000, -4.0, 1.0), # Upper mids (cut)
            EqualizerBand(2500, 2.0, 1.0),  # Presence
            EqualizerBand(6300, 4.0, 1.0),  # Brilliance
            EqualizerBand(16000, 6.0, 1.0), # Air
        ]
    )
    
    print("Applying V-shaped EQ...")
    player.set_filters(config)
    
    for _ in range(150):
        frame = player.read_frame()
        time.sleep(0.02)
    
    print("  ✓ V-shaped EQ applied\n")


def demo_combined_effects(player: spence.Player):
    """Demo combining multiple effects"""
    
    print("\nCombined Effects Demo\n")
    
    # Vibey electronic sound
    config = FilterConfig(
        speed=0.95,
        pitch=0.95,
        equalizer=[
            EqualizerBand(60, 5.0, 1.0),
            EqualizerBand(12000, 3.0, 1.0),
        ],
        tremolo_enabled=True,
        tremolo_frequency=4.0,
        tremolo_depth=0.3,
        rotation_enabled=True,
        rotation_speed=0.15,
    )
    
    print("Applying combined effects (slow + bass + tremolo + rotation)...")
    player.set_filters(config)
    
    for _ in range(150):
        frame = player.read_frame()
        time.sleep(0.02)
    
    print("  ✓ Combined effects applied\n")


def main():
    print("spence Audio Filters Demo")
    print("=" * 50)
    
    # Setup
    node = spence.Node()
    
    print("\nResolving track...")
    track = node.resolve("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    print(f"Loaded: {track.artist} - {track.title}\n")
    
    player = node.create_player()
    player.load(track)
    player.play()
    
    # Demo presets
    demo_presets(player)
    
    # Demo custom EQ
    demo_custom_eq(player)
    
    # Demo combined effects
    demo_combined_effects(player)
    
    # Clear filters
    print("\nClearing Filters\n")
    player.set_filters(Filters.clear())
    
    for _ in range(150):
        frame = player.read_frame()
        time.sleep(0.02)
    
    print("  ✓ Filters cleared\n")
    
    # Show metrics
    metrics = player.metrics()
    print("\nFinal Metrics:")
    print(f"  Frames generated: {metrics.frames_generated}")
    print(f"  Frames dropped: {metrics.frames_dropped}")
    print(f"  Avg frame time: {metrics.avg_frame_time_us}µs")
    
    # Cleanup
    player.stop()
    node.shutdown()
    
    print("\nDemo complete!")


if __name__ == "__main__":
    main()
