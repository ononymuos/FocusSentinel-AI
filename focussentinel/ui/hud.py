import cv2
import cvzone
from typing import Tuple, List, Dict, Any
from ..core.state import FocusState, SessionMetrics
from ..config import SentinelConfig

class HUDVisualizer:
    """Renders a clean, cyber-minimalist HUD overlay onto video frames."""
    
    def __init__(self, config: SentinelConfig):
        self.config = config
        
    def draw(self, frame, state: FocusState, metrics: SessionMetrics, phone_detections: List[Dict[str, Any]]) -> any:
        """Renders status badges, telemetry bars, and alerts on top of the frame."""
        if not self.config.show_hud:
            return frame
            
        # 1. Draw Target Detections (e.g., Phone)
        if self.config.show_bounding_boxes:
            for det in phone_detections:
                x1, y1, x2, y2 = det["box"]
                conf = int(det["confidence"] * 100)
                label = f"{det['class'].upper()} ({conf}%)"
                cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 215), 2)
                cvzone.putTextRect(frame, label, (x1, max(30, y1 - 10)), scale=1, thickness=1, colorR=(255, 0, 215))
                
        # 2. Status Badge Top-Left
        badge_text = "FOCUS: ACTIVE"
        badge_color = (46, 204, 113)  # Green
        
        if state == FocusState.READING_OR_WRITING:
            badge_text = "MODE: READING / STUDYING"
            badge_color = (243, 156, 18)  # Blue/Orange
        elif state == FocusState.MICRO_SLEEP:
            badge_text = "ALERT: DROWSINESS DETECTED"
            badge_color = (0, 0, 255)
        elif state == FocusState.FACE_ABSENT:
            badge_text = "ALERT: USER ABSENT / COVERED"
            badge_color = (50, 50, 50)
        elif state == FocusState.PHONE_DISTRACTION:
            badge_text = "ALERT: PHONE USAGE DETECTED"
            badge_color = (0, 140, 255)
            
        cvzone.putTextRect(frame, badge_text, (30, 40), scale=1.2, thickness=2, colorR=badge_color)
        
        # 3. Telemetry Bar
        telemetry = f"Eye Ratio: {metrics.current_eye_ratio:.1f}% | Pitch: {metrics.current_pitch:.1f}* | Focus: {metrics.focus_score:.1f}%"
        cvzone.putTextRect(frame, telemetry, (30, 80), scale=0.9, thickness=1, colorR=(30, 30, 30))
        
        # 4. Large Warning Banners for Active Alerts
        if state == FocusState.MICRO_SLEEP:
            cvzone.putTextRect(frame, "SLEEP ALERT - WAKE UP!", (60, 160), scale=2.2, thickness=3, colorR=(0, 0, 255))
        elif state == FocusState.FACE_ABSENT:
            cvzone.putTextRect(frame, "FACE NOT DETECTED!", (60, 160), scale=2.2, thickness=3, colorR=(0, 0, 200))
        elif state == FocusState.PHONE_DISTRACTION:
            cvzone.putTextRect(frame, "PUT PHONE AWAY!", (60, 160), scale=2.2, thickness=3, colorR=(0, 140, 255))
            
        # 5. Watermark / Author Credit (Bottom-Right)
        h, w = frame.shape[:2]
        cv2.putText(
            frame,
            "FocusSentinel AI | (c) Usama Baig",
            (w - 280, h - 15),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.45,
            (180, 180, 180),
            1,
            cv2.LINE_AA
        )
            
        return frame
