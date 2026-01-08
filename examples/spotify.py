import spence


def main():
    node = spence.Node()
    
    # Resolve Spotify track
    print("Resolving Spotify track...")
    track = node.resolve("https://open.spotify.com/track/3n3Ppam7vgaVa1iaRUc9Lp")
    
    print(f"\nResolved:")
    print(f"  Title: {track.title}")
    print(f"  Artist: {track.artist}")
    print(f"  Duration: {track.duration_seconds:.1f}s")
    print(f"  Original platform: {track.platform}")
    print(f"  Resolved to: {track.stream_url[:50]}...")
    
    # Search Spotify
    print("\n\nSearching Spotify...")
    results = node.search("spotify:bohemian rhapsody queen", limit=5)
    
    print(f"\nFound {len(results)} results:")
    for i, track in enumerate(results, 1):
        print(f"  {i}. {track.artist} - {track.title} ({track.duration_seconds:.0f}s)")
    
    node.shutdown()


if __name__ == "__main__":
    main()
