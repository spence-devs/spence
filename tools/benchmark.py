#!/usr/bin/env python3

import time
import statistics
from client import Node


def benchmark_resolution(node: Node, urls: list[str], iterations: int = 10):
    """Benchmark resolver performance"""
    print(f"\nBenchmarking resolution ({iterations} iterations)...")
    
    timings = []
    for url in urls:
        for _ in range(iterations):
            start = time.perf_counter()
            try:
                track = node.resolve(url)
                elapsed = time.perf_counter() - start
                timings.append(elapsed)
            except Exception as e:
                print(f"Failed to resolve {url}: {e}")
    
    if timings:
        print(f"  Mean: {statistics.mean(timings)*1000:.2f}ms")
        print(f"  Median: {statistics.median(timings)*1000:.2f}ms")
        print(f"  Min: {min(timings)*1000:.2f}ms")
        print(f"  Max: {max(timings)*1000:.2f}ms")


def benchmark_frame_generation(node: Node, duration_seconds: int = 10):
    """Benchmark frame generation rate"""
    print(f"\nBenchmarking frame generation ({duration_seconds}s)...")
    
    player = node.create_player()
    
    # Dummy track
    from client.api.track import Track
    track = Track(
        id="test",
        title="Test",
        artist="Test",
        duration=duration_seconds * 1000,
        stream_url="test://null",
        platform="test"
    )
    
    player.load(track)
    player.play()
    
    start = time.perf_counter()
    frames = 0
    
    while time.perf_counter() - start < duration_seconds:
        frame = player.read_frame()
        if frame:
            frames += 1
    
    elapsed = time.perf_counter() - start
    fps = frames / elapsed
    
    print(f"  Frames: {frames}")
    print(f"  FPS: {fps:.2f}")
    print(f"  Expected: 50 FPS (20ms frames)")


def main():
    print("spence performance benchmark")
    print("=" * 40)
    
    node = Node()
    
    test_urls = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    ]
    
    benchmark_resolution(node, test_urls)
    
    node.shutdown()


if __name__ == "__main__":
    main()
