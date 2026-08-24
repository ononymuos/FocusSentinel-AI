import logging
import os
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

class AudioManager:
    """Manages multi-channel sound alerts with immediate interrupt capability."""
    
    def __init__(self, audio_paths: dict, default_volume: float = 0.8):
        self.audio_paths = audio_paths
        self.volume = default_volume
        self.sounds = {}
        self.current_playing: Optional[str] = None
        self.enabled = True
        self._init_mixer()
        
    def _init_mixer(self):
        try:
            import pygame
            pygame.mixer.init()
            for key, path in self.audio_paths.items():
                if path and Path(path).exists():
                    sound = pygame.mixer.Sound(str(path))
                    sound.set_volume(self.volume)
                    self.sounds[key] = sound
                else:
                    logger.warning(f"Audio alert '{key}' file not found at: {path}")
        except Exception as e:
            logger.error(f"Failed to initialize pygame mixer: {e}")
            self.enabled = False
            
    def play_alert(self, alert_key: str):
        """Plays sound alert on loop with zero latency and instant previous cutoff."""
        if not self.enabled:
            return
            
        if self.current_playing == alert_key:
            return  # Already playing
            
        self.stop_all()
        
        if alert_key in self.sounds:
            try:
                self.sounds[alert_key].play(-1)
                self.current_playing = alert_key
            except Exception as e:
                logger.error(f"Error playing sound '{alert_key}': {e}")
                
    def stop_all(self):
        """Instantly interrupts and silences all running audio."""
        if not self.enabled:
            return
        try:
            import pygame
            pygame.mixer.stop()
            self.current_playing = None
        except Exception as e:
            logger.error(f"Error stopping mixer: {e}")
            
    def set_volume(self, volume: float):
        self.volume = max(0.0, min(1.0, volume))
        for sound in self.sounds.values():
            sound.set_volume(self.volume)
