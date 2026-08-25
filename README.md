# FocusSentinel AI

[![Release](https://img.shields.io/github/v/release/ononymuos/FocusSentinel-AI?style=for-the-badge&color=00e5ff)](https://github.com/ononymuos/FocusSentinel-AI/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-blue?style=for-the-badge)](https://github.com/ononymuos/FocusSentinel-AI)

Computer vision focus and study session monitor built with Python, OpenCV, MediaPipe, and YOLOv8.

FocusSentinel AI tracks user alertness, reading posture, phone distractions, and desk absence in real time. It uses 3D head pose estimation and eye aspect ratio analysis to differentiate between active studying (looking down at a notebook) and actual drowsiness, preventing false alarms.

---

## 📥 Installation & Quick Start

Choose your operating system below for copy-paste installation commands:

### 🪟 Windows Installation

#### Option A: One-Click Standalone Installer (Recommended — No Python Required)
Download and run the official Windows setup wizard from [GitHub Releases](https://github.com/ononymuos/FocusSentinel-AI/releases/latest):

```powershell
# PowerShell: Download & Run Installer
Invoke-WebRequest -Uri "https://github.com/ononymuos/FocusSentinel-AI/releases/download/v1.0.0/FocusSentinel_Setup_v1.0.0.exe" -OutFile "FocusSentinel_Setup_v1.0.0.exe"
Start-Process ".\FocusSentinel_Setup_v1.0.0.exe"
```

```cmd
:: Command Prompt (CMD): Download & Run Installer
curl -LO https://github.com/ononymuos/FocusSentinel-AI/releases/download/v1.0.0/FocusSentinel_Setup_v1.0.0.exe
start FocusSentinel_Setup_v1.0.0.exe
```

#### Option B: Manual Source Installation

```powershell
# PowerShell
git clone https://github.com/ononymuos/FocusSentinel-AI.git
cd FocusSentinel-AI
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt customtkinter
python main.py
```

```cmd
:: Command Prompt (CMD)
git clone https://github.com/ononymuos/FocusSentinel-AI.git
cd FocusSentinel-AI
python -m venv .venv
call .venv\Scripts\activate.bat
pip install -r requirements.txt customtkinter
python main.py
```

---

### 🐧 Linux Installation (Ubuntu, Debian, Arch, Fedora)

Run the one-line terminal installer to install FocusSentinel AI, configure a dedicated virtual environment, create the `focussentinel` CLI binary, and register the application in your Desktop App Launcher menu:

```bash
# One-click automated setup
curl -sSL https://raw.githubusercontent.com/ononymuos/FocusSentinel-AI/main/install_linux.sh | bash
```

*Or clone and run manually:*
```bash
git clone https://github.com/ononymuos/FocusSentinel-AI.git
cd FocusSentinel-AI
chmod +x install_linux.sh
./install_linux.sh
```

To start: launch **FocusSentinel AI** from your application menu or run `~/.local/bin/focussentinel`.

---

### 🍎 macOS Installation (Apple Silicon M1/M2/M3/M4 & Intel)

```bash
# One-click automated setup
curl -sSL https://raw.githubusercontent.com/ononymuos/FocusSentinel-AI/main/install_macos.sh | bash
```

*Or clone and run manually:*
```bash
git clone https://github.com/ononymuos/FocusSentinel-AI.git
cd FocusSentinel-AI
chmod +x install_macos.sh
./install_macos.sh
```

To start: launch **FocusSentinel AI** from `~/Applications` or run `~/.local/bin/focussentinel`.

---

## 🎛️ Modern Desktop Control Center GUI

FocusSentinel AI includes an in-app GUI control center built with CustomTkinter:

- **Vision Detection Toggles**: Individual On/Off switches for Micro-Sleep Detection, YOLOv8 Phone Distraction, Absence Tracking, and Real-time HUD.
- **Custom Audio Selector**: Directly browse and load custom `.mp3`, `.wav`, or `.ogg` sound files for Sleep, Phone, and Absence alarms with live **▶ Test** audio preview buttons.
- **Audio Control System**: Master mute switch, master volume slider (0%–100%), and independent audio channel toggles.
- **Live Telemetry & Diagnostics**: Real-time Focus Score percentage, active focus duration timer, distraction event counter, and 3D head pitch angle gauge.
- **Hardware Source Selector**: In-app camera device index selector with instant switching.

---

- **Author / Creator**: [Usama Baig](https://github.com/ononymuos)
- **Repository**: [https://github.com/ononymuos/FocusSentinel-AI](https://github.com/ononymuos/FocusSentinel-AI)
- **LinkedIn**: [Usama Baig](https://www.linkedin.com/in/usama-baig-53b828385)

### Giving Credit
If you use, modify, reference, or embed FocusSentinel AI in your research, commercial applications, or open-source projects, please provide attribution by including the copyright notice and linking back to the original repository:

```text
FocusSentinel AI by Usama Baig (https://github.com/ononymuos/FocusSentinel-AI)
Copyright (c) 2026 Usama Baig. All rights reserved.
```

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

## License & Copyright

Distributed under the MIT License.

Copyright (c) 2026 **Usama Baig**. All rights reserved.

See [`LICENSE`](LICENSE) for full legal text and conditions. In accordance with the license, the above copyright and permission notice must be included in all copies or substantial portions of this software.
