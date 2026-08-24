#!/usr/bin/env python3
"""
FocusSentinel AI - Main CLI Entry Point
"""
import cv2
import argparse
import sys
from pathlib import Path

from focussentinel.config import SentinelConfig
from focussentinel.engine import FocusSentinelEngine
from focussentinel.core.state import FocusState

def main():
    parser = argparse.ArgumentParser(
        description="FocusSentinel AI - Real-time Vision Focus & Attention Monitor",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("--camera", type=int, default=0, help="Camera device index")
    parser.add_argument("--mute", action="store_true", help="Mute sound alarms")
    parser.add_argument("--no-hud", action="store_true", help="Disable HUD overlay")
    parser.add_argument("--phone-conf", type=float, default=0.5, help="Phone detection confidence threshold")
    parser.add_argument("--reading-pitch", type=float, default=-10.0, help="Downwards pitch threshold in degrees for reading posture")
    
    args = parser.parse_args()
    
    config = SentinelConfig(
        camera_index=args.camera,
        audio_muted=args.mute,
        show_hud=not args.no_hud,
        phone_confidence_threshold=args.phone_conf,
        reading_pitch_threshold=args.reading_pitch
    )
    
    print("=" * 60)
    print("  🛡️  FocusSentinel AI - Intelligent Focus Monitor")
    print("  Copyright (c) 2026 Usama Baig. All rights reserved.")
    print("  https://github.com/ononymuos/FocusSentinel-AI")
    print("=" * 60)
    print(f"[*] Camera Source: #{config.camera_index}")
    print(f"[*] Audio Alarms: {'DISABLED (Muted)' if config.audio_muted else 'ENABLED'}")
    print(f"[*] Pitch Threshold: {config.reading_pitch_threshold} deg")
    print("[*] Press 'q' to quit, 'm' to toggle mute, 'r' to reset metrics.\n")
    
    cap = cv2.VideoCapture(config.camera_index)
    if not cap.isOpened():
        print(f"[!] Error: Could not open camera {config.camera_index}", file=sys.stderr)
        sys.exit(1)
        
    engine = FocusSentinelEngine(config)
    engine.start_session()
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("[!] Failed to grab camera frame. Exiting.")
                break
                
            processed_frame, state, metrics = engine.process_frame(frame)
            
            cv2.imshow("FocusSentinel AI", processed_frame)
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q') or key == 27:  # ESC or q
                break
            elif key == ord('m'):
                config.audio_muted = not config.audio_muted
                print(f"[*] Mute toggled: {config.audio_muted}")
            elif key == ord('r'):
                engine.metrics = engine.metrics.__class__()
                engine.metrics.start()
                print("[*] Session metrics reset.")
                
    except KeyboardInterrupt:
        print("\n[*] Stopping...")
    finally:
        engine.stop_session()
        cap.release()
        cv2.destroyAllWindows()
        
        print("\n" + "=" * 60)
        print("  📊 Session Summary Analytics")
        print("=" * 60)
        print(f"  Total Elapsed:    {engine.metrics.elapsed_seconds:.1f} seconds")
        print(f"  Active Focus:     {engine.metrics.total_focus_seconds:.1f} seconds")
        print(f"  Reading / Notes:  {engine.metrics.total_reading_seconds:.1f} seconds")
        print(f"  Distracted:       {engine.metrics.total_distracted_seconds:.1f} seconds")
        print(f"  Focus Score:      {engine.metrics.focus_score:.1f}%")
        print(f"  Sleep Events:     {engine.metrics.sleep_events_count}")
        print(f"  Phone Events:     {engine.metrics.phone_events_count}")
        print(f"  Absence Events:   {engine.metrics.absence_events_count}")
        print("=" * 60)

if __name__ == "__main__":
    main()
