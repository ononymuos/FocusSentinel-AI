# FocusSentinel AI

Computer vision focus and study session monitor built with Python, OpenCV, and YOLOv8.

FocusSentinel AI tracks user alertness, reading posture, phone distractions, and desk absence in real time. It uses 3D head pose estimation and eye aspect ratio analysis to differentiate between active studying (looking down at a notebook) and actual drowsiness, preventing false alarms.

---

## Core capabilities

- **Drowsiness and micro-sleep tracking**: Measures eye aspect ratio (EAR) to detect prolonged eye closure.
- **3D head pose estimation**: Calculates pitch, yaw, and roll via `cv2.solvePnP`. Downward head angles (pitch < -10 deg) are classified as reading or writing notes rather than sleep.
- **Phone detection**: Employs YOLOv8 object detection to catch unauthorized phone usage during work sessions.
- **Absence alerts**: Monitors continuous face visibility to alert when the user steps away or covers the camera.
- **Instant audio cutoffs**: Dedicated audio manager interrupts alarms the exact moment a distraction condition clears.
- **Modular architecture**: Clean separation between vision modules, audio triggers, telemetry metrics, and the HUD overlay. Ready for custom desktop GUIs (PyQt, CustomTkinter, Tauri, Electron).

---

## Project architecture

```text
FocusSentinel-AI/
├── assets/
│   ├── audio/              # Sound alerts (sleep, absence, phone)
│   └── models/             # YOLOv8 weights and MediaPipe task assets
├── focussentinel/
│   ├── audio/              # Multi-channel audio mixer with instant interrupt
│   ├── core/               # State machine, focus metrics, and session timers
│   ├── ui/                 # Cyber-minimalist HUD overlay visualizer
│   ├── vision/             # Face mesh, 3D head pose solver, YOLO distraction detector
│   ├── config.py           # Centralized configuration dataclass
│   └── engine.py           # Core orchestrator and event pipeline
├── main.py                 # CLI entry point
├── setup.py                # Package installation script
├── requirements.txt        # Runtime dependencies
└── README.md
```

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/ononymuos/FocusSentinel-AI.git
cd FocusSentinel-AI
```

### 2. Set up environment

```bash
# Using standard venv
python -m venv .venv

# Activate on Windows:
.venv\Scripts\activate

# Activate on Linux / macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## Usage

Run the monitor with default settings:

```bash
python main.py
```

### CLI options

| Flag | Type | Default | Description |
|---|---|---|---|
| `--camera` | int | `0` | Camera device index |
| `--mute` | flag | `False` | Disable sound alerts |
| `--no-hud` | flag | `False` | Hide on-screen telemetry overlay |
| `--phone-conf` | float | `0.5` | Minimum confidence score for phone detection |
| `--reading-pitch` | float | `-10.0` | Head angle cutoff in degrees for note reading |

### Keyboard shortcuts

- `q` or `ESC`: Quit application and print session summary analytics.
- `m`: Toggle audio alerts (mute / unmute).
- `r`: Reset session focus score and metrics.

---

## Customizing alerts

You can replace the default audio files in `assets/audio/` with your own `.mp3` files:

- `assets/audio/sleep_alarm.mp3`: Plays when micro-sleep is detected.
- `assets/audio/face_hidden.mp3`: Plays when the user is absent or the face is covered.
- `assets/audio/phone_alert.mp3`: Plays when a phone enters the frame.

---

## Embedding in custom desktop apps

The engine is designed to be imported directly into PyQt, CustomTkinter, or web-based wrappers:

```python
import cv2
from focussentinel import FocusSentinelEngine, SentinelConfig, FocusState

config = SentinelConfig(camera_index=0, audio_volume=0.9)
engine = FocusSentinelEngine(config)
engine.start_session()

cap = cv2.VideoCapture(0)
while True:
    ret, frame = cap.read()
    if not ret:
        break
    annotated_frame, current_state, metrics = engine.process_frame(frame)
    
    # Hook into your GUI frame painter or dashboard
    if current_state == FocusState.PHONE_DISTRACTION:
        print(f"Distraction detected! Focus score: {metrics.focus_score:.1f}%")
```

---

## License

Distributed under the MIT License. See `LICENSE` for details.
