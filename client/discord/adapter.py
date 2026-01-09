import struct
from typing import Optional


class RTPPacketBuilder:
    """Stateful RTP packet builder for Discord voice
    
    Maintains sequence numbers and timestamps according to RFC 3550.
    Discord uses RTP payload type 0x78 for Opus.
    """
    
    # Discord RTP constants
    RTP_VERSION = 2
    PAYLOAD_TYPE = 0x78  # Discord Opus
    HEADER_SIZE = 12
    SAMPLES_PER_FRAME = 960  # 20ms at 48kHz
    
    def __init__(self, ssrc: int):
        """
        Args:
            ssrc: Synchronization source identifier from Discord
        """
        self._ssrc = ssrc
        self._sequence = 0
        self._timestamp = 0
    
    def build_packet(self, opus_data: bytes) -> bytes:
        """Construct RTP packet with current state
        
        Args:
            opus_data: Encoded Opus frame
            
        Returns:
            Complete RTP packet ready for transmission
        """
        header = bytearray(self.HEADER_SIZE)
        
        # Byte 0: Version (2 bits) + Padding (1) + Extension (1) + CSRC count (4)
        # V=2, P=0, X=0, CC=0
        header[0] = self.RTP_VERSION << 6
        
        # Byte 1: Marker (1 bit) + Payload type (7 bits)
        # M=0 for continuous audio
        header[1] = self.PAYLOAD_TYPE
        
        # Bytes 2-3: Sequence number (big endian)
        struct.pack_into('>H', header, 2, self._sequence)
        
        # Bytes 4-7: Timestamp (big endian)
        struct.pack_into('>I', header, 4, self._timestamp)
        
        # Bytes 8-11: SSRC (big endian)
        struct.pack_into('>I', header, 8, self._ssrc)
        
        return bytes(header) + opus_data
    
    def advance(self) -> None:
        """Advance sequence and timestamp for next frame
        
        Called after each packet is sent.
        """
        self._sequence = (self._sequence + 1) & 0xFFFF
        self._timestamp = (self._timestamp + self.SAMPLES_PER_FRAME) & 0xFFFFFFFF
    
    def reset(self) -> None:
        """Reset state (for stream restart)"""
        self._sequence = 0
        self._timestamp = 0
    
    @property
    def sequence(self) -> int:
        """Current sequence number"""
        return self._sequence
    
    @property
    def timestamp(self) -> int:
        """Current timestamp"""
        return self._timestamp


def create_rtp_packet(opus_data: bytes, sequence: int, timestamp: int, ssrc: int) -> bytes:
    """Legacy function for backward compatibility
    
    Prefer using RTPPacketBuilder for stateful operation.
    """
    builder = RTPPacketBuilder(ssrc)
    builder._sequence = sequence
    builder._timestamp = timestamp
    return builder.build_packet(opus_data)
