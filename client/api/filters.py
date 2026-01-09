from dataclasses import dataclass
from typing import Optional


@dataclass
class EqualizerBand:
    """Single equalizer band"""
    frequency: float  # Hz
    gain: float  # dB (-15 to +15)
    bandwidth: float = 1.0  # Octaves


@dataclass
class FilterConfig:
    """Audio filter configuration"""
    
    # Volume
    volume: float = 1.0
    
    # Equalizer (15 bands)
    equalizer: Optional[list[EqualizerBand]] = None
    
    # Karaoke
    karaoke_enabled: bool = False
    karaoke_level: float = 1.0
    karaoke_mono_level: float = 1.0
    karaoke_filter_band: float = 220.0
    karaoke_filter_width: float = 100.0
    
    # Timescale
    speed: float = 1.0
    pitch: float = 1.0
    rate: float = 1.0
    
    # Tremolo
    tremolo_enabled: bool = False
    tremolo_frequency: float = 2.0
    tremolo_depth: float = 0.5
    
    # Vibrato
    vibrato_enabled: bool = False
    vibrato_frequency: float = 2.0
    vibrato_depth: float = 0.5
    
    # Rotation
    rotation_enabled: bool = False
    rotation_speed: float = 0.0
    
    # Distortion
    distortion_enabled: bool = False
    distortion_sin_offset: float = 0.0
    distortion_sin_scale: float = 1.0
    distortion_cos_offset: float = 0.0
    distortion_cos_scale: float = 1.0
    distortion_tan_offset: float = 0.0
    distortion_tan_scale: float = 1.0
    distortion_offset: float = 0.0
    distortion_scale: float = 1.0
    
    # Channel mix
    left_to_left: float = 1.0
    left_to_right: float = 0.0
    right_to_left: float = 0.0
    right_to_right: float = 1.0
    
    # Low pass
    low_pass_enabled: bool = False
    low_pass_smoothing: float = 20.0
    
    def to_native(self):
        """Convert to native filter config"""
        from client.bridge.core import NativeFilterConfig
        
        config = NativeFilterConfig()
        config.volume = self.volume
        config.speed = self.speed
        config.pitch = self.pitch
        
        if self.equalizer:
            for band in self.equalizer:
                config.add_equalizer_band(band.frequency, band.gain, band.bandwidth)
        
        config.karaoke_enabled = self.karaoke_enabled
        config.karaoke_level = self.karaoke_level
        
        config.tremolo_enabled = self.tremolo_enabled
        config.tremolo_frequency = self.tremolo_frequency
        config.tremolo_depth = self.tremolo_depth
        
        config.vibrato_enabled = self.vibrato_enabled
        config.vibrato_frequency = self.vibrato_frequency
        config.vibrato_depth = self.vibrato_depth
        
        config.rotation_enabled = self.rotation_enabled
        config.rotation_speed = self.rotation_speed
        
        config.distortion_enabled = self.distortion_enabled
        config.low_pass_enabled = self.low_pass_enabled
        
        return config


class Filters:
    """Common filter presets"""
    
    @staticmethod
    def nightcore() -> FilterConfig:
        """Nightcore effect (higher pitch, faster)"""
        return FilterConfig(
            speed=1.3,
            pitch=1.3,
            rate=1.0
        )
    
    @staticmethod
    def vaporwave() -> FilterConfig:
        """Vaporwave effect (lower pitch, slower)"""
        return FilterConfig(
            speed=0.8,
            pitch=0.8,
            rate=1.0,
            tremolo_enabled=True,
            tremolo_frequency=3.0,
            tremolo_depth=0.3
        )
    
    @staticmethod
    def bassboost(level: float = 0.25) -> FilterConfig:
        """Bass boost effect"""
        gain = level * 15.0  # Scale to dB
        return FilterConfig(
            equalizer=[
                EqualizerBand(25, gain, 1.0),
                EqualizerBand(40, gain * 0.9, 1.0),
                EqualizerBand(63, gain * 0.8, 1.0),
                EqualizerBand(100, gain * 0.6, 1.0),
                EqualizerBand(160, gain * 0.4, 1.0),
            ]
        )
    
    @staticmethod
    def soft() -> FilterConfig:
        """Soft audio (reduced high frequencies)"""
        return FilterConfig(
            low_pass_enabled=True,
            low_pass_smoothing=15.0
        )
    
    @staticmethod
    def tremolo(frequency: float = 4.0, depth: float = 0.5) -> FilterConfig:
        """Tremolo effect"""
        return FilterConfig(
            tremolo_enabled=True,
            tremolo_frequency=frequency,
            tremolo_depth=depth
        )
    
    @staticmethod
    def vibrato(frequency: float = 10.0, depth: float = 0.9) -> FilterConfig:
        """Vibrato effect"""
        return FilterConfig(
            vibrato_enabled=True,
            vibrato_frequency=frequency,
            vibrato_depth=depth
        )
    
    @staticmethod
    def rotation(speed: float = 0.2) -> FilterConfig:
        """8D audio rotation"""
        return FilterConfig(
            rotation_enabled=True,
            rotation_speed=speed
        )
    
    @staticmethod
    def karaoke() -> FilterConfig:
        """Karaoke mode (reduce vocals)"""
        return FilterConfig(
            karaoke_enabled=True,
            karaoke_level=1.0,
            karaoke_mono_level=1.0,
            karaoke_filter_band=220.0,
            karaoke_filter_width=100.0
        )
    
    @staticmethod
    def clear() -> FilterConfig:
        """Clear all filters"""
        return FilterConfig()
