import struct


def create_rtp_packet(opus_data: bytes, sequence: int, timestamp: int, ssrc: int) -> bytes:
    """Build RTP packet for Discord voice"""
    
    # RTP header (12 bytes)
    # Version=2, Padding=0, Extension=0, CSRC=0
    # Marker=0, PayloadType=0x78 (Discord Opus)
    
    header = bytearray(12)
    
    # Byte 0: Version (2 bits) = 2
    header[0] = 0x80
    
    # Byte 1: Payload type = 0x78
    header[1] = 0x78
    
    # Bytes 2-3: Sequence number (big endian)
    struct.pack_into('>H', header, 2, sequence)
    
    # Bytes 4-7: Timestamp (big endian)
    struct.pack_into('>I', header, 4, timestamp)
    
    # Bytes 8-11: SSRC (big endian)
    struct.pack_into('>I', header, 8, ssrc)
    
    # Append Opus payload
    return bytes(header) + opus_data
