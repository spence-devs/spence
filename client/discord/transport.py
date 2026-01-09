import asyncio
from time import perf_counter
from client.api.player import Player
from client.discord.adapter import RTPPacketBuilder


class AudioTransport:
    """Manages timing-accurate audio transmission to Discord
    
    Maintains strict 20ms frame intervals with drift correction.
    """
    
    def __init__(self, voice_client, player: Player):
        self._voice = voice_client
        self._player = player
        self._running = False
        
        # RTP state
        self._rtp = RTPPacketBuilder(voice_client.ssrc)
        
        # Timing
        self._frame_duration = 0.020  # 20ms
        self._next_frame_time = 0.0
    
    async def run(self) -> None:
        """Main transmission loop with precise timing"""
        self._running = True
        self._next_frame_time = perf_counter()
        
        missed_frames = 0
        
        while self._running:
            now = perf_counter()
            
            # Check if we're behind schedule
            if now > self._next_frame_time + self._frame_duration:
                missed_frames += 1
                # Hard resync if too far behind
                if missed_frames > 5:
                    self._next_frame_time = now
                    missed_frames = 0
            
            # Read frame from player
            frame = self._player.read_frame()
            
            if frame:
                # Build and send RTP packet
                packet = self._rtp.build_packet(frame)
                self._voice.send_audio_packet(packet)
                
                missed_frames = 0
            else:
                # Send silence frame to maintain timing
                silence = b'\xf8\xff\xfe'  # Opus silence frame
                packet = self._rtp.build_packet(silence)
                self._voice.send_audio_packet(packet)
            
            # Advance RTP state
            self._rtp.advance()
            
            # Schedule next frame
            self._next_frame_time += self._frame_duration
            
            # Sleep until next frame time
            sleep_time = self._next_frame_time - perf_counter()
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)
            else:
                # Yield to event loop even if behind
                await asyncio.sleep(0)
    
    def stop(self) -> None:
        """Stop transmission"""
        self._running = False
