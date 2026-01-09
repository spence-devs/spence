import discord
from discord.ext import commands
import spence


bot = commands.Bot(command_prefix=".", intents=discord.Intents.default())
node = spence.Node()

# Store active voice clients per guild
voice_clients = {}
players = {}


@bot.event
async def on_ready():
    print(f"Bot ready as {bot.user}")


@bot.command()
async def play(ctx, *, query: str):
    """Play a track"""
    
    if not ctx.author.voice:
        await ctx.send("You must be in a voice channel!")
        return
    
    voice_channel = ctx.author.voice.channel
    
    # Connect to voice if not already connected
    if ctx.guild.id not in voice_clients:
        discord_voice = await voice_channel.connect()
    else:
        discord_voice = voice_clients[ctx.guild.id]._voice
    
    await ctx.send(f"Searching for: {query}")
    
    try:
        track = node.resolve(query)
    except spence.TrackNotFound:
        await ctx.send("Track not found!")
        return
    
    # Stop existing player if any
    if ctx.guild.id in voice_clients:
        await voice_clients[ctx.guild.id].disconnect()
    
    # Create new player
    player = node.create_player()
    player.load(track)
    player.play()
    
    # Create voice client (handles RTP automatically)
    vc = spence.VoiceClient(discord_voice, player)
    await vc.connect()
    
    # Store references
    voice_clients[ctx.guild.id] = vc
    players[ctx.guild.id] = player
    
    await ctx.send(f"Now playing: {track.artist} - {track.title}")


@bot.command()
async def pause(ctx):
    """Pause playback"""
    if ctx.guild.id in players:
        players[ctx.guild.id].pause()
        await ctx.send("⏸ Paused")
    else:
        await ctx.send("Nothing playing!")


@bot.command()
async def resume(ctx):
    """Resume playback"""
    if ctx.guild.id in players:
        players[ctx.guild.id].play()
        await ctx.send("▶ Resumed")
    else:
        await ctx.send("Nothing paused!")


@bot.command()
async def volume(ctx, vol: int):
    """Set volume (0-200)"""
    if ctx.guild.id in players:
        volume = max(0, min(200, vol)) / 100.0
        players[ctx.guild.id].set_volume(volume)
        await ctx.send(f"🔊 Volume set to {vol}%")
    else:
        await ctx.send("Nothing playing!")


@bot.command()
async def seek(ctx, position: str):
    """Seek to position (MM:SS)"""
    if ctx.guild.id not in players:
        await ctx.send("Nothing playing!")
        return
    
    try:
        parts = position.split(":")
        if len(parts) == 2:
            minutes, seconds = int(parts[0]), int(parts[1])
            position_ms = (minutes * 60 + seconds) * 1000
            players[ctx.guild.id].seek(position_ms)
            await ctx.send(f"⏩ Seeked to {position}")
        else:
            await ctx.send("Use format MM:SS")
    except ValueError:
        await ctx.send("Invalid time format!")


@bot.command()
async def bassboost(ctx, level: int = 25):
    """Apply bass boost (0-100)"""
    if ctx.guild.id in players:
        boost_level = max(0, min(100, level)) / 100.0
        players[ctx.guild.id].set_filters(spence.Filters.bassboost(boost_level))
        await ctx.send(f"🔊 Bass boost: {level}%")
    else:
        await ctx.send("Nothing playing!")


@bot.command()
async def nightcore(ctx):
    """Apply nightcore effect"""
    if ctx.guild.id in players:
        players[ctx.guild.id].set_filters(spence.Filters.nightcore())
        await ctx.send("🎵 Nightcore effect applied!")
    else:
        await ctx.send("Nothing playing!")


@bot.command()
async def vaporwave(ctx):
    """Apply vaporwave effect"""
    if ctx.guild.id in players:
        players[ctx.guild.id].set_filters(spence.Filters.vaporwave())
        await ctx.send("🌊 Vaporwave effect applied!")
    else:
        await ctx.send("Nothing playing!")


@bot.command()
async def rotation(ctx):
    """Apply 8D rotation effect"""
    if ctx.guild.id in players:
        players[ctx.guild.id].set_filters(spence.Filters.rotation())
        await ctx.send("🎧 8D rotation effect applied!")
    else:
        await ctx.send("Nothing playing!")


@bot.command()
async def clear_filters(ctx):
    """Remove all audio filters"""
    if ctx.guild.id in players:
        players[ctx.guild.id].set_filters(spence.Filters.clear())
        await ctx.send("🔄 Filters cleared")
    else:
        await ctx.send("Nothing playing!")


@bot.command()
async def stop(ctx):
    """Stop playback and disconnect"""
    if ctx.guild.id in voice_clients:
        await voice_clients[ctx.guild.id].disconnect()
        
        if ctx.guild.id in players:
            players[ctx.guild.id].stop()
        
        # Disconnect from voice
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
        
        # Clean up references
        voice_clients.pop(ctx.guild.id, None)
        players.pop(ctx.guild.id, None)
        
        await ctx.send("⏹ Stopped and disconnected")
    else:
        await ctx.send("Nothing playing!")


@bot.command()
async def nowplaying(ctx):
    """Show current track"""
    if ctx.guild.id in players:
        player = players[ctx.guild.id]
        track = player.current_track
        
        if track:
            position = player.position_ms / 1000
            duration = track.duration_seconds
            
            progress = int((position / duration) * 20)
            bar = "▬" * progress + "🔘" + "▬" * (20 - progress)
            
            time_str = f"{int(position//60)}:{int(position%60):02d} / {int(duration//60)}:{int(duration%60):02d}"
            
            await ctx.send(
                f"🎵 Now Playing\n"
                f"**{track.artist} - {track.title}**\n"
                f"{bar}\n"
                f"`{time_str}`"
            )
        else:
            await ctx.send("Nothing loaded!")
    else:
        await ctx.send("Nothing playing!")


if __name__ == "__main__":
    import os
    
    TOKEN = os.getenv("DISCORD_TOKEN")
    if not TOKEN:
        print("Set DISCORD_TOKEN environment variable")
        exit(1)
    
    bot.run(TOKEN)
