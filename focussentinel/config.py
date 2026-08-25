import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Tuple

BASE_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = BASE_DIR / "assets"

@dataclass
class SentinelConfig:
    """Centralized configuration for FocusSentinel engine."""
    
    # Camera Settings
    camera_index: int = 0
    frame_width: int = 1280
    frame_height: int = 720
    target_fps: int = 30
    
    # Model Paths
    yolo_model_path: Path = field(default_factory=lambda: ASSETS_DIR / "models" / "yolov8n.pt")
    face_landmarker_path: Path = field(default_factory=lambda: ASSETS_DIR / "models" / "face_landmarker.task")
    
    # Audio Paths
    audio_sleep_path: Path = field(default_factory=lambda: ASSETS_DIR / "audio" / "sleep_alarm.mp3")
    audio_face_hidden_path: Path = field(default_factory=lambda: ASSETS_DIR / "audio" / "face_hidden.mp3")
    audio_phone_path: Path = field(default_factory=lambda: ASSETS_DIR / "audio" / "phone_alert.mp3")
    audio_volume: float = 0.8
    audio_muted: bool = False
    
    # Feature Toggles (Vision & Distraction detectors)
    enable_sleep_detection: bool = True
    enable_phone_detection: bool = True
    enable_absence_detection: bool = True
    
    # Feature Toggles (Individual Audio Alarms)
    enable_sleep_audio: bool = True
    enable_phone_audio: bool = True
    enable_absence_audio: bool = True
    
    # Vision & Pose Thresholds
    eye_ratio_threshold: float = 11.0          # Eye Aspect Ratio cutoff percentage
    reading_pitch_threshold: float = -10.0     # Pitch in degrees (< -10 = looking down into desk/notebook)
    sleep_threshold_frames: int = 60           # ~2.0s at 30 FPS
    face_cover_threshold_frames: int = 120      # ~4.0s at 30 FPS
    
    # Object Detection Settings
    phone_confidence_threshold: float = 0.5
    target_classes: List[str] = field(default_factory=lambda: ["cell phone"])
    
    # Visual HUD Settings
    show_hud: bool = True
    show_landmarks: bool = False
    show_bounding_boxes: bool = True
    theme_color_active: Tuple[int, int, int] = (46, 204, 113)     # Emerald Green
    theme_color_reading: Tuple[int, int, int] = (52, 152, 219)    # Blue
    theme_color_warning: Tuple[int, int, int] = (241, 196, 15)    # Yellow
    theme_color_danger: Tuple[int, int, int] = (231, 76, 60)      # Crimson Red
