import cv2
import numpy as np
from typing import Tuple, List

# 3D generic facial anthropometric points
MODEL_POINTS_3D = np.array([
    (0.0, 0.0, 0.0),             # Nose tip
    (0.0, -330.0, -65.0),        # Chin
    (-225.0, 170.0, -135.0),     # Left eye outer corner
    (225.0, 170.0, -135.0),      # Right eye outer corner
    (-150.0, -150.0, -125.0),    # Left mouth corner
    (150.0, -150.0, -125.0)      # Right mouth corner
], dtype=np.float64)

# Key landmark indices: Nose tip (1), Chin (152), Left eye outer (33), Right eye outer (263), Left mouth (61), Right mouth (291)
POSE_LANDMARKS_INDICES = [1, 152, 33, 263, 61, 291]

class HeadPoseEstimator:
    """Solves 3D Perspective-n-Point (PnP) problem to estimate 3-DOF head angles (Pitch, Yaw, Roll)."""
    
    def __init__(self):
        self.dist_coeffs = np.zeros((4, 1))
        
    def estimate_pose(self, face_landmarks: List, frame_shape: Tuple[int, int, int]) -> Tuple[float, float, float]:
        """
        Calculates pitch, yaw, and roll in degrees.
        Negative Pitch = Looking downward (reading/writing notes).
        Positive Pitch = Looking upward.
        """
        h, w, _ = frame_shape
        focal_length = float(w)
        center = (w / 2.0, h / 2.0)
        camera_matrix = np.array([
            [focal_length, 0.0, center[0]],
            [0.0, focal_length, center[1]],
            [0.0, 0.0, 1.0]
        ], dtype=np.float64)
        
        try:
            image_points = []
            for idx in POSE_LANDMARKS_INDICES:
                pt = face_landmarks[idx]
                image_points.append([float(pt[0]), float(pt[1])])
            image_points = np.array(image_points, dtype=np.float64)
            
            success, rot_vec, trans_vec = cv2.solvePnP(
                MODEL_POINTS_3D,
                image_points,
                camera_matrix,
                self.dist_coeffs,
                flags=cv2.SOLVEPNP_ITERATIVE
            )
            if not success:
                return 0.0, 0.0, 0.0
                
            rmat, _ = cv2.Rodrigues(rot_vec)
            angles, _, _, _, _, _ = cv2.RQDecomp3x3(rmat)
            
            pitch = angles[0] * 360.0
            yaw = angles[1] * 360.0
            roll = angles[2] * 360.0
            return pitch, yaw, roll
        except Exception:
            return 0.0, 0.0, 0.0
