from enum import Enum, auto
from dataclasses import dataclass
import time

class FocusState(Enum):
    FOCUSED = auto()
    READING_OR_WRITING = auto()
    MICRO_SLEEP = auto()
    FACE_ABSENT = auto()
    PHONE_DISTRACTION = auto()

@dataclass
class SessionMetrics:
    """Real-time and cumulative statistics for study session analytics."""
    session_start_time: float = 0.0
    total_focus_seconds: float = 0.0
    total_reading_seconds: float = 0.0
    total_distracted_seconds: float = 0.0
    sleep_events_count: int = 0
    absence_events_count: int = 0
    phone_events_count: int = 0
    
    current_state: FocusState = FocusState.FOCUSED
    current_pitch: float = 0.0
    current_yaw: float = 0.0
    current_roll: float = 0.0
    current_eye_ratio: float = 0.0
    
    def start(self):
        self.session_start_time = time.time()
        
    @property
    def elapsed_seconds(self) -> float:
        if self.session_start_time == 0.0:
            return 0.0
        return time.time() - self.session_start_time
        
    @property
    def focus_score(self) -> float:
        total = self.elapsed_seconds
        if total <= 0:
            return 100.0
        productive = self.total_focus_seconds + self.total_reading_seconds
        return min(100.0, max(0.0, (productive / total) * 100.0))
