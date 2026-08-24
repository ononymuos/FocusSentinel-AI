from typing import Tuple, List, Optional
from cvzone.FaceMeshModule import FaceMeshDetector

# Left Eye & Face width landmark markers
LEFT_EYE_TOP = 159
LEFT_EYE_BOTTOM = 145
FACE_LEFT = 130
FACE_RIGHT = 243

class FaceAnalyzer:
    """Performs facial landmark detection, EAR calculation, and face presence evaluation."""
    
    def __init__(self, max_faces: int = 1):
        self.detector = FaceMeshDetector(maxFaces=max_faces)
        
    def process_frame(self, frame, draw: bool = False) -> Tuple[any, List]:
        """Detects face mesh landmarks from frame."""
        return self.detector.findFaceMesh(frame, draw=draw)
        
    def calculate_eye_ratio(self, face_landmarks: List) -> float:
        """Calculates normalized Eye Aspect Ratio (EAR) relative to face dimension."""
        try:
            eye_dist, _ = self.detector.findDistance(face_landmarks[LEFT_EYE_TOP], face_landmarks[LEFT_EYE_BOTTOM])
            face_dist, _ = self.detector.findDistance(face_landmarks[FACE_LEFT], face_landmarks[FACE_RIGHT])
            if face_dist == 0:
                return 0.0
            return (eye_dist / face_dist) * 100.0
        except Exception:
            return 0.0
