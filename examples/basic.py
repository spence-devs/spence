import spence
import time


def main():
    # Create node
    node = spence.Node(thread_pool_size=4)
    
    # Resolve track
    print("Resolving track...")
    track = node.resolve("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    
    print(f"Title: {track.title}")
    print(f"Artist: {track.artist}")
    print(f"Duration: {track.duration_seconds:.1f}s")
    print(f"Platform: {track.platform}")
    
    # Create player
    player = node.create_player()
    
    # Load and play
    print("\nLoading track...")
    player.load(track)
    
    print("Playing...")
    player.play()
    
    # Read frames for 10 seconds
    duration = 10
    frames = 0
    
    start = time.time()
    while time.time() - start < duration:
        frame = player.read_frame()
        if frame:
            frames += 1
            # In real usage, send frame to Discord voice gateway
        time.sleep(0.02)  # 20ms frame rate
    
    print(f"\nGenerated {frames} frames in {duration}s")
    
    # Show metrics
    metrics = player.metrics()
    print(f"\nMetrics:")
    print(f"  Frames generated: {metrics.frames_generated}")
    print(f"  Frames dropped: {metrics.frames_dropped}")
    print(f"  Decode errors: {metrics.decode_errors}")
    print(f"  Avg frame time: {metrics.avg_frame_time_us}µs")
    
    # Cleanup
    player.stop()
    node.shutdown()


if __name__ == "__main__":
    main()
