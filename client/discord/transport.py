import asyncio
from client.api.player import Player
from client.discord.adapter import create_rtp_packet


class AudioTransport:
    """Manages audio transmission to Discord"""
    
    def __init__(self, voice_client, player: Player):
        self._voice = voice_client
        self._player = player
        self._running = False
        self._sequence = 0
        self._timestamp = 0
    
    async def run(self) -> None:
        """Main transmission loop"""
        self._running = True
        
        while self._running:
            # Read frame from player
            frame = self._player.read_frame()
            
            if frame:
                # Build RTP packet
                packet = create_rtp_packet(
                    frame,
                    self._sequence,
                    self._timestamp,
                    self._voice.ssrc
                )
                
                # Send to Discord
                self._voice.send_audio_packet(packet)
                
                # Update sequence and timestamp
                self._sequence = (self._sequence + 1) % 65536
                self._timestamp = (self._timestamp + 960) % (2**32)
            
            # Wait for next frame (20ms)
            await asyncio.sleep(0.02)
    
    def stop(self) -> None:
        """Stop transmission"""
        self._running = False
