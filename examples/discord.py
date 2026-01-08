import discord
from discord.ext import commands
import spence


bot = commands.Bot(command_prefix=".", intents=discord.Intents.default())
node = spence.Node()


@bot.event
async def on_ready():
    print(f"Bot ready as {bot.user}")


@bot.command()
async def play(ctx, *, query: str):
    """Play a track"""
    
    # Join voice channel
    if not ctx.author.voice:
        await ctx.send("You must be in a voice channel!")
        return
    
    voice_channel = ctx.author.voice.channel
    
    if not ctx.voice_client:
        voice_client = await voice_channel.connect()
    else:
        voice_client = ctx.voice_client
    
    # Resolve track
    await ctx.send(f"Searching for: {query}")
    
    try:
        track = node.resolve(query)
    except spence.TrackNotFound:
        await ctx.send("Track not found!")
        return
    
    # Create player and queue
    player = node.create_player()
    player.load(track)
    
    # Wrap with spence voice client
    vc = spence.VoiceClient(voice_client, player)
    await vc.connect()
    
    player.play()
    
    await ctx.send(f"Now playing: {track.artist} - {track.title}")


@bot.command()
async def pause(ctx):
    """Pause playback"""
    # Implementation depends on storing player reference
    await ctx.send("Paused")


@bot.command()
async def stop(ctx):
    """Stop playback and disconnect"""
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
    await ctx.send("Stopped")


@bot.command()
async def queue(ctx, *, query: str):
    """Add track to queue"""
    track = node.resolve(query)
    # Queue implementation
    await ctx.send(f"Added to queue: {track.title}")


if __name__ == "__main__":
    import os
    
    TOKEN = os.getenv("DISCORD_TOKEN")
    if not TOKEN:
        print("Set DISCORD_TOKEN environment variable")
        exit(1)
    
    bot.run(TOKEN)
