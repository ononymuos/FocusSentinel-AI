import cv2
import time
import logging
from typing import Optional, Callable, Dict, Any, Tuple

from .config import SentinelConfig
from .core.state import FocusState, SessionMetrics
from .vision.head_pose import HeadPoseEstimator
from .vision.face_mesh import FaceAnalyzer
from .vision.detector import ObjectDistractionDetector
from .audio.manager import AudioManager
from .ui.hud import HUDVisualizer

logger = logging.getLogger(__name__)

class FocusSentinelEngine:
    """
    Core orchestrator for real-time focus & attention monitoring.
    Designed for standalone execution, background workers, or integration
    into desktop GUIs (PyQt, CustomTkinter, Electron, Tauri).
    """
    
    def __init__(self, config: Optional[SentinelConfig] = None):
        self.config = config or SentinelConfig()
        self.metrics = SessionMetrics()
        
        # Initialize subsystems
        self.face_analyzer = FaceAnalyzer(max_faces=1)
        self.pose_estimator = HeadPoseEstimator()
        self.object_detector = ObjectDistractionDetector(
            model_path=self.config.yolo_model_path,
            target_classes=self.config.target_classes,
            conf_threshold=self.config.phone_confidence_threshold
        )
        
        audio_map = {
            "sleep": self.config.audio_sleep_path,
            "face_hidden": self.config.audio_face_hidden_path,
            "phone": self.config.audio_phone_path,
        }
        self.audio_manager = AudioManager(audio_map, default_volume=self.config.audio_volume)
        self.hud = HUDVisualizer(self.config)
        
        # Frame counters & state tracking
        self._closed_frames = 0
        self._covered_frames = 0
        self._phone_frames = 0
        self._frame_count = 0
        self._cached_phone_detections = []
        self._is_running = False
        self._last_tick_time = time.time()
        
        # Event callback for GUI listeners
        self.state_change_callback: Optional[Callable[[FocusState, SessionMetrics], None]] = None
        
    def start_session(self):
        """Starts session tracking."""
        self._is_running = True
        self.metrics.start()
        self._last_tick_time = time.time()
        
    def stop_session(self):
        """Stops session tracking and silences audio."""
        self._is_running = False
        self.audio_manager.stop_all()
        
    def process_frame(self, frame) -> Tuple[Any, FocusState, SessionMetrics]:
        """
        Processes an incoming video frame:
        1. Extracts face mesh & head pose.
        2. Evaluates Eye Aspect Ratio (EAR) + pitch angle.
        3. Detects phone / unauthorized objects.
        4. Updates session metrics & audio triggers.
        5. Renders HUD overlay.
        
        Returns (processed_frame, current_state, metrics)
        """
        now = time.time()
        dt = max(0.001, now - self._last_tick_time)
        self._last_tick_time = now
        
        # 1. Face Mesh & Pose
        frame, faces = self.face_analyzer.process_frame(frame, draw=self.config.show_landmarks)
        
        is_reading = False
        is_sleepy = False
        is_face_covered = False
        pitch, yaw, roll = 0.0, 0.0, 0.0
        ratio = 0.0
        
        if faces:
            self._covered_frames = 0
            face = faces[0]
            
            pitch, yaw, roll = self.pose_estimator.estimate_pose(face, frame.shape)
            if pitch < self.config.reading_pitch_threshold:
                is_reading = True
                
            ratio = self.face_analyzer.calculate_eye_ratio(face)
            
            # Evaluate Micro-Sleep with decay buffer against single-frame flickers
            if self.config.enable_sleep_detection and not is_reading and ratio < self.config.eye_ratio_threshold:
                self._closed_frames = min(self._closed_frames + 2, self.config.sleep_threshold_frames + 10)
            else:
                self._closed_frames = max(0, self._closed_frames - 1)
                
            if self.config.enable_sleep_detection and self._closed_frames >= self.config.sleep_threshold_frames:
                is_sleepy = True
        else:
            self._closed_frames = 0
            self._covered_frames += 1
            if self.config.enable_absence_detection and self._covered_frames >= self.config.face_cover_threshold_frames:
                is_face_covered = True
                
        # 2. Object Distraction Detection (Phone) with throttling & temporal persistence
        self._frame_count += 1
        if self.config.enable_phone_detection:
            interval = max(1, getattr(self.config, 'yolo_inference_interval', 3))
            if self._frame_count % interval == 0:
                self._cached_phone_detections = self.object_detector.detect(frame)
            phone_detections = self._cached_phone_detections
        else:
            self._cached_phone_detections = []
            phone_detections = []
            
        raw_phone_detected = len(phone_detections) > 0
        persistence = max(1, getattr(self.config, 'phone_persistence_frames', 3))
        if raw_phone_detected:
            self._phone_frames = min(self._phone_frames + 1, persistence + 5)
        else:
            self._phone_frames = max(0, self._phone_frames - 1)
            
        phone_detected = self._phone_frames >= persistence
        
        # 3. Determine Focus State
        previous_state = self.metrics.current_state
        if is_face_covered:
            new_state = FocusState.FACE_ABSENT
            self.metrics.absence_events_count += 1 if previous_state != FocusState.FACE_ABSENT else 0
        elif is_sleepy:
            new_state = FocusState.MICRO_SLEEP
            self.metrics.sleep_events_count += 1 if previous_state != FocusState.MICRO_SLEEP else 0
        elif phone_detected:
            new_state = FocusState.PHONE_DISTRACTION
            self.metrics.phone_events_count += 1 if previous_state != FocusState.PHONE_DISTRACTION else 0
        elif is_reading:
            new_state = FocusState.READING_OR_WRITING
        else:
            new_state = FocusState.FOCUSED
            
        # Update cumulative duration metrics
        if new_state in (FocusState.FOCUSED,):
            self.metrics.total_focus_seconds += dt
        elif new_state == FocusState.READING_OR_WRITING:
            self.metrics.total_reading_seconds += dt
        else:
            self.metrics.total_distracted_seconds += dt
            
        self.metrics.current_state = new_state
        self.metrics.current_pitch = pitch
        self.metrics.current_yaw = yaw
        self.metrics.current_roll = roll
        self.metrics.current_eye_ratio = ratio
        
        # 4. Audio Control Trigger
        if not self.config.audio_muted:
            if new_state == FocusState.FACE_ABSENT and self.config.enable_absence_audio:
                self.audio_manager.play_alert("face_hidden")
            elif new_state == FocusState.MICRO_SLEEP and self.config.enable_sleep_audio:
                self.audio_manager.play_alert("sleep")
            elif new_state == FocusState.PHONE_DISTRACTION and self.config.enable_phone_audio:
                self.audio_manager.play_alert("phone")
            else:
                self.audio_manager.stop_all()
        else:
            self.audio_manager.stop_all()
            
        # State change callback
        if new_state != previous_state and self.state_change_callback:
            self.state_change_callback(new_state, self.metrics)
            
        # 5. Render HUD
        annotated_frame = self.hud.draw(frame, new_state, self.metrics, phone_detections)
        return annotated_frame, new_state, self.metrics

