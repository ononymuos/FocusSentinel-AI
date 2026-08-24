import logging
from pathlib import Path
from typing import List, Dict, Any
from ultralytics import YOLO

logger = logging.getLogger(__name__)

class ObjectDistractionDetector:
    """Detects unauthorized distraction objects (e.g., cell phones) using YOLOv8."""
    
    def __init__(self, model_path: Path, target_classes: List[str] = None, conf_threshold: float = 0.5):
        self.model_path = model_path
        self.target_classes = target_classes or ["cell phone"]
        self.conf_threshold = conf_threshold
        self.model = YOLO(str(model_path))
        self.class_names = self.model.names
        
    def detect(self, frame) -> List[Dict[str, Any]]:
        """Runs inference on frame and returns bounding boxes of detected target distraction objects."""
        results = self.model.predict(frame, stream=True, verbose=False)
        detections = []
        
        for r in results:
            for box in r.boxes:
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                name = self.class_names.get(cls_id, "")
                
                if name in self.target_classes and conf >= self.conf_threshold:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    detections.append({
                        "class": name,
                        "confidence": conf,
                        "box": (x1, y1, x2, y2)
                    })
        return detections
