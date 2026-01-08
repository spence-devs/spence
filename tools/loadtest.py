#!/usr/bin/env python3

import time
import psutil
import os
from client import Node
from client.api.track import Track


def create_test_track() -> Track:
    """Create a test track"""
    return Track(
        id="test",
        title="Load Test Track",
        artist="spence",
        duration=300000,  # 5 minutes
        stream_url="test://null",
        platform="test"
    )


def measure_memory() -> float:
    """Get current process memory in MB"""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024


def load_test(num_players: int, duration_seconds: int = 60):
    """Test concurrent player load"""
    print(f"Load test: {num_players} concurrent players for {duration_seconds}s")
    print("=" * 60)
    
    node = Node(thread_pool_size=8)
    track = create_test_track()
    
    # Create players
    print(f"Creating {num_players} players...")
    players = []
    
    initial_mem = measure_memory()
    
    for i in range(num_players):
        player = node.create_player()
        player.load(track)
        player.play()
        players.append(player)
        
        if (i + 1) % 100 == 0:
            mem = measure_memory()
            print(f"  {i+1} players created, memory: {mem:.1f}MB")
    
    loaded_mem = measure_memory()
    print(f"\nMemory after loading: {loaded_mem:.1f}MB")
    print(f"Memory per player: {(loaded_mem - initial_mem) / num_players:.2f}MB")
    
    # Run for duration
    print(f"\nRunning for {duration_seconds}s...")
    start = time.time()
    
    while time.time() - start < duration_seconds:
        time.sleep(5)
        
        # Sample metrics
        mem = measure_memory()
        cpu = psutil.Process(os.getpid()).cpu_percent(interval=1)
        
        total_frames = sum(p.metrics().frames_generated for p in players)
        total_dropped = sum(p.metrics().frames_dropped for p in players)
        
        print(f"  Time: {time.time()-start:.1f}s, "
              f"Memory: {mem:.1f}MB, "
              f"CPU: {cpu:.1f}%, "
              f"Frames: {total_frames}, "
              f"Dropped: {total_dropped}")
    
    # Stop all players
    print("\nStopping players...")
    for player in players:
        player.stop()
    
    final_mem = measure_memory()
    print(f"\nFinal memory: {final_mem:.1f}MB")
    print(f"Memory growth during test: {final_mem - loaded_mem:.1f}MB")
    
    node.shutdown()
    print("\nLoad test complete!")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Load test spence")
    parser.add_argument("--players", type=int, default=100, help="Number of concurrent players")
    parser.add_argument("--duration", type=int, default=60, help="Test duration in seconds")
    
    args = parser.parse_args()
    
    load_test(args.players, args.duration)


if __name__ == "__main__":
    main()
