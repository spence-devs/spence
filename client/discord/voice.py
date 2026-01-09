import asyncio
from typing import Optional
from client.api.player import Player
from client.discord.transport import AudioTransport


class VoiceClient:
    """PDiscord voice integration
    
    Handles RTP packet construction and voice transmission.
    User only needs to provide discord.VoiceClient and spence.Player.
    """
    
    def __init__(self, voice_client, player: Player):
        """
        Args:
            voice_client: discord.VoiceClient instance from discord.py
            player: spence.Player instance
        """
        self._voice = voice_client
        self._player = player
        self._transport: Optional[AudioTransport] = None
        self._task: Optional[asyncio.Task] = None
        self._connected = False
    
    async def connect(self) -> None:
        """Start audio transmission to Discord"""
        if self._connected:
            return
        
        self._transport = AudioTransport(self._voice, self._player)
        self._task = asyncio.create_task(self._transport.run())
        self._connected = True
    
    async def disconnect(self) -> None:
        """Stop audio transmission"""
        if not self._connected:
            return
        
        self._connected = False
        
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None
        
        if self._transport:
            self._transport.stop()
            self._transport = None
    
    @property
    def is_connected(self) -> bool:
        """Whether actively transmitting audio"""
        return self._connected and self._voice.is_connected()
    
    async def __aenter__(self):
        """Context manager support"""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager cleanup"""
        await self.disconnect()
