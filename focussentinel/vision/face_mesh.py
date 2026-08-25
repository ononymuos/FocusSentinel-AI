from typing import Tuple, List, Optional
from cvzone.FaceMeshModule import FaceMeshDetector

# Left Eye landmarks (top, bottom, left/outer corner, right/inner corner)
LEFT_EYE_TOP = 159
LEFT_EYE_BOTTOM = 145
LEFT_EYE_OUTER = 33
LEFT_EYE_INNER = 133

# Right Eye landmarks (top, bottom, left/inner corner, right/outer corner)
RIGHT_EYE_TOP = 386
RIGHT_EYE_BOTTOM = 374
RIGHT_EYE_INNER = 362
RIGHT_EYE_OUTER = 263

# Reference inter-pupillary / outer corners for fallback
FACE_LEFT = 130
FACE_RIGHT = 243

class FaceAnalyzer:
    """Performs facial landmark detection, robust dual-eye EAR calculation, and face presence evaluation."""
    
    def __init__(self, max_faces: int = 1):
        self.detector = FaceMeshDetector(maxFaces=max_faces)
        
    def process_frame(self, frame, draw: bool = False) -> Tuple[any, List]:
        """Detects face mesh landmarks from frame."""
        return self.detector.findFaceMesh(frame, draw=draw)
        
    def calculate_eye_ratio(self, face_landmarks: List) -> float:
        """
        Calculates robust normalized Eye Aspect Ratio (EAR) averaged across both eyes.
        Uses local eye width as the primary normalizer to remain invariant to head yaw/turns.
        Falls back gracefully if one eye is obscured.
        """
        try:
            ratios = []
            
            # Left Eye calculation
            left_v, _ = self.detector.findDistance(face_landmarks[LEFT_EYE_TOP], face_landmarks[LEFT_EYE_BOTTOM])
            left_h, _ = self.detector.findDistance(face_landmarks[LEFT_EYE_OUTER], face_landmarks[LEFT_EYE_INNER])
            if left_h > 0:
                ratios.append((left_v / left_h) * 100.0)
                
            # Right Eye calculation
            right_v, _ = self.detector.findDistance(face_landmarks[RIGHT_EYE_TOP], face_landmarks[RIGHT_EYE_BOTTOM])
            right_h, _ = self.detector.findDistance(face_landmarks[RIGHT_EYE_INNER], face_landmarks[RIGHT_EYE_OUTER])
            if right_h > 0:
                ratios.append((right_v / right_h) * 100.0)
                
            if ratios:
                return float(sum(ratios) / len(ratios))
                
            # Fallback to global face width if eye corners couldn't be resolved
            face_dist, _ = self.detector.findDistance(face_landmarks[FACE_LEFT], face_landmarks[FACE_RIGHT])
            if face_dist > 0:
                return float((left_v / face_dist) * 100.0)
                
            return 0.0
        except Exception:
            return 0.0
