import asyncio
from typing import Optional
from client.api.player import Player
from client.discord.transport import AudioTransport


class VoiceClient:
    """Wrapper around discord.py voice client"""
    
    def __init__(self, voice_client, player: Player):
        """
        Args:
            voice_client: discord.VoiceClient instance
            player: spence Player instance
        """
        self._voice = voice_client
        self._player = player
        self._transport: Optional[AudioTransport] = None
        self._task: Optional[asyncio.Task] = None
    
    async def connect(self) -> None:
        """Start audio transmission"""
        self._transport = AudioTransport(self._voice, self._player)
        self._task = asyncio.create_task(self._transport.run())
    
    async def disconnect(self) -> None:
        """Stop audio transmission"""
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        
        if self._transport:
            self._transport.stop()
    
    @property
    def is_connected(self) -> bool:
        """Whether connected to voice"""
        return self._voice.is_connected()
