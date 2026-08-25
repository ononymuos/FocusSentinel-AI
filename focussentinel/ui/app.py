"""
FocusSentinel AI - Modern Desktop Control Center GUI
Built with CustomTkinter & OpenCV
"""
import os
import sys
import time
import threading
from pathlib import Path
from tkinter import filedialog, messagebox
import customtkinter as ctk
from PIL import Image, ImageTk
import cv2
import pygame

from focussentinel.config import SentinelConfig
from focussentinel.engine import FocusSentinelEngine
from focussentinel.core.state import FocusState

# Configure CustomTkinter Theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

# Fix Windows Taskbar AppUserModelID so custom icon displays on Taskbar
try:
    import ctypes
    app_id = "ononymuos.focussentinel.ai.v1"
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
except Exception:
    pass

class FocusSentinelApp(ctk.CTk):
    def __init__(self, config: SentinelConfig = None):
        super().__init__()
        
        self.config = config or SentinelConfig()
        self.engine = FocusSentinelEngine(self.config)
        self.cap = None
        self.is_running = False
        self.thread = None
        
        # Window Setup
        self.title("FocusSentinel AI - Sentinel Command Center")
        self.geometry("1280x820")
        self.minsize(1100, 750)
        
        # Set window & taskbar icon
        self._set_app_icon()
                
        self._build_ui()
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        
    def _set_app_icon(self):
        base_dir = Path(__file__).resolve().parent.parent.parent
        icon_ico = base_dir / "icon.ico"
        icon_png = base_dir / "icon.png"
        
        # Check direct or sys._MEIPASS for PyInstaller
        if hasattr(sys, '_MEIPASS'):
            meipass_dir = Path(sys._MEIPASS)
            if (meipass_dir / "icon.ico").exists():
                icon_ico = meipass_dir / "icon.ico"
            if (meipass_dir / "icon.png").exists():
                icon_png = meipass_dir / "icon.png"
                
        if icon_ico.exists():
            try:
                self.iconbitmap(str(icon_ico))
            except Exception:
                pass
                
        if icon_png.exists():
            try:
                img = Image.open(icon_png)
                photo = ImageTk.PhotoImage(img)
                self.wm_iconphoto(True, photo)
                self._icon_photo_ref = photo  # Keep reference so it doesn't get garbage collected
            except Exception:
                pass
        
    def _build_ui(self):
        # Main Grid Layout (2 Columns: Left = Video/Telemetry, Right = Control Panel)
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(0, weight=1)
        
        # =========================================================================
        # LEFT FRAME: Video Viewport & Real-time Telemetry
        # =========================================================================
        self.left_frame = ctk.CTkFrame(self, corner_radius=12, fg_color="#11141a")
        self.left_frame.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")
        self.left_frame.grid_rowconfigure(1, weight=1)
        self.left_frame.grid_columnconfigure(0, weight=1)
        
        # Header Banner
        header_box = ctk.CTkFrame(self.left_frame, fg_color="transparent")
        header_box.grid(row=0, column=0, padx=20, pady=(15, 5), sticky="ew")
        
        title_lbl = ctk.CTkLabel(
            header_box, 
            text="🛡️ FocusSentinel AI", 
            font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
            text_color="#00e5ff"
        )
        title_lbl.pack(side="left")
        
        self.status_badge = ctk.CTkLabel(
            header_box,
            text="● STANDBY",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color="#9ba1a6",
            fg_color="#1e232d",
            corner_radius=6,
            padx=12,
            pady=4
        )
        self.status_badge.pack(side="right")
        
        # Video Feed Canvas
        self.video_frame = ctk.CTkFrame(self.left_frame, fg_color="#0b0d11", corner_radius=10)
        self.video_frame.grid(row=1, column=0, padx=15, pady=10, sticky="nsew")
        self.video_frame.grid_rowconfigure(0, weight=1)
        self.video_frame.grid_columnconfigure(0, weight=1)
        
        self.video_label = ctk.CTkLabel(self.video_frame, text="Camera feed standby\nClick 'Start Sentinel Session' to begin", font=ctk.CTkFont(size=15), text_color="#5f6368")
        self.video_label.grid(row=0, column=0, sticky="nsew")
        
        # Live Telemetry Cards
        telemetry_box = ctk.CTkFrame(self.left_frame, fg_color="#161b22", corner_radius=10)
        telemetry_box.grid(row=2, column=0, padx=15, pady=(5, 15), sticky="ew")
        telemetry_box.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        # Stat 1: Focus Score
        self.card_focus = self._create_stat_card(telemetry_box, 0, "Focus Score", "100%", "#00e676")
        # Stat 2: Active Focus Time
        self.card_time = self._create_stat_card(telemetry_box, 1, "Focused Time", "00:00", "#00e5ff")
        # Stat 3: Distractions
        self.card_distractions = self._create_stat_card(telemetry_box, 2, "Distractions", "0", "#ffab00")
        # Stat 4: Head Pitch
        self.card_pitch = self._create_stat_card(telemetry_box, 3, "Head Pitch", "0.0°", "#80d8ff")
        
        # =========================================================================
        # RIGHT FRAME: Master Controls & Customization Dashboard (Scrollable)
        # =========================================================================
        self.right_frame = ctk.CTkScrollableFrame(self, corner_radius=12, fg_color="#161b22")
        self.right_frame.grid(row=0, column=1, padx=(0, 15), pady=15, sticky="nsew")
        self.right_frame.grid_columnconfigure(0, weight=1)
        
        # Section: Session Actions
        action_box = ctk.CTkFrame(self.right_frame, fg_color="transparent")
        action_box.pack(fill="x", padx=10, pady=(5, 15))
        
        self.btn_start = ctk.CTkButton(
            action_box,
            text="▶ Start Sentinel Session",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#00c853",
            hover_color="#00e676",
            height=40,
            command=self.toggle_session
        )
        self.btn_start.pack(fill="x", pady=(0, 6))
        
        self.btn_reset = ctk.CTkButton(
            action_box,
            text="🔄 Reset Session Stats",
            font=ctk.CTkFont(size=13),
            fg_color="#263238",
            hover_color="#37474f",
            height=32,
            command=self.reset_session
        )
        self.btn_reset.pack(fill="x")
        
        # -------------------------------------------------------------------------
        # Section 1: Vision Feature Switches (Enable/Disable Detection Modules)
        # -------------------------------------------------------------------------
        self._create_section_header(self.right_frame, "👁️ Vision Detection Modules")
        vision_box = ctk.CTkFrame(self.right_frame, fg_color="#1f242d", corner_radius=8)
        vision_box.pack(fill="x", padx=10, pady=5)
        
        self.sw_sleep_det = self._create_switch(vision_box, "Drowsiness & Micro-Sleep Tracking", self.config.enable_sleep_detection, self._on_toggle_sleep_det)
        self.sw_phone_det = self._create_switch(vision_box, "YOLOv8 Phone Distraction Detection", self.config.enable_phone_detection, self._on_toggle_phone_det)
        self.sw_abs_det = self._create_switch(vision_box, "Absence & Desk Departure Detection", self.config.enable_absence_detection, self._on_toggle_abs_det)
        self.sw_hud = self._create_switch(vision_box, "On-Screen HUD Visualizer Overlay", self.config.show_hud, self._on_toggle_hud)
        
        # -------------------------------------------------------------------------
        # Section 2: Audio Alarms & Sound Customizer
        # -------------------------------------------------------------------------
        self._create_section_header(self.right_frame, "🔊 Audio Alert Triggers & Custom Sounds")
        audio_box = ctk.CTkFrame(self.right_frame, fg_color="#1f242d", corner_radius=8)
        audio_box.pack(fill="x", padx=10, pady=5)
        
        # Master Mute
        self.sw_master_audio = self._create_switch(audio_box, "Master Sound System Enabled", not self.config.audio_muted, self._on_toggle_master_audio)
        
        # Volume Slider
        vol_row = ctk.CTkFrame(audio_box, fg_color="transparent")
        vol_row.pack(fill="x", padx=15, pady=(5, 10))
        ctk.CTkLabel(vol_row, text="Master Volume:", font=ctk.CTkFont(size=12, weight="bold")).pack(side="left")
        self.lbl_vol = ctk.CTkLabel(vol_row, text=f"{int(self.config.audio_volume*100)}%", font=ctk.CTkFont(size=12))
        self.lbl_vol.pack(side="right")
        self.slider_vol = ctk.CTkSlider(audio_box, from_=0.0, to=1.0, number_of_steps=100, command=self._on_vol_change)
        self.slider_vol.set(self.config.audio_volume)
        self.slider_vol.pack(fill="x", padx=15, pady=(0, 15))
        
        # Sound Slot 1: Sleep Alarm
        self.sw_sleep_snd = self._create_switch(audio_box, "Sleep Alarm Sound", self.config.enable_sleep_audio, self._on_toggle_sleep_snd)
        self.picker_sleep = self._create_sound_picker(audio_box, "sleep", self.config.audio_sleep_path)
        
        # Sound Slot 2: Phone Alert
        self.sw_phone_snd = self._create_switch(audio_box, "Phone Alert Sound", self.config.enable_phone_audio, self._on_toggle_phone_snd)
        self.picker_phone = self._create_sound_picker(audio_box, "phone", self.config.audio_phone_path)
        
        # Sound Slot 3: Absence / Covered Face Alert
        self.sw_abs_snd = self._create_switch(audio_box, "Absence / Face Hidden Sound", self.config.enable_absence_audio, self._on_toggle_abs_snd)
        self.picker_abs = self._create_sound_picker(audio_box, "face_hidden", self.config.audio_face_hidden_path)
        
        # -------------------------------------------------------------------------
        # Section 3: Fine-Tuning Sensitivity Sliders
        # -------------------------------------------------------------------------
        self._create_section_header(self.right_frame, "⚙️ Sensitivity & Thresholds")
        sliders_box = ctk.CTkFrame(self.right_frame, fg_color="#1f242d", corner_radius=8)
        sliders_box.pack(fill="x", padx=10, pady=5)
        
        # Phone Confidence Slider
        self.slider_phone_conf = self._create_slider_control(
            sliders_box, 
            "Phone Confidence Threshold", 
            0.2, 0.9, self.config.phone_confidence_threshold, 
            "%0.2f", 
            self._on_phone_conf_change
        )
        
        # Reading Pitch Threshold Slider
        self.slider_pitch_thresh = self._create_slider_control(
            sliders_box, 
            "Reading Downward Pitch Angle", 
            -30.0, 0.0, self.config.reading_pitch_threshold, 
            "%0.1f°", 
            self._on_pitch_thresh_change
        )
        
        # Camera Source Picker
        cam_row = ctk.CTkFrame(sliders_box, fg_color="transparent")
        cam_row.pack(fill="x", padx=15, pady=10)
        ctk.CTkLabel(cam_row, text="Camera Index / Device:", font=ctk.CTkFont(size=12, weight="bold")).pack(side="left")
        self.opt_camera = ctk.CTkOptionMenu(cam_row, values=["0", "1", "2", "3"], width=70, command=self._on_camera_select)
        self.opt_camera.set(str(self.config.camera_index))
        self.opt_camera.pack(side="right")

    # =========================================================================
    # Helper UI Builders
    # =========================================================================
    def _create_stat_card(self, parent, col, title, initial_val, color):
        card = ctk.CTkFrame(parent, fg_color="transparent")
        card.grid(row=0, column=col, padx=8, pady=8, sticky="ew")
        lbl_title = ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=11), text_color="#9ba1a6")
        lbl_title.pack()
        lbl_val = ctk.CTkLabel(card, text=initial_val, font=ctk.CTkFont(size=16, weight="bold"), text_color=color)
        lbl_val.pack()
        return lbl_val
        
    def _create_section_header(self, parent, text):
        header = ctk.CTkLabel(
            parent, 
            text=text, 
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#00e5ff",
            anchor="w"
        )
        header.pack(fill="x", padx=12, pady=(12, 4))
        
    def _create_switch(self, parent, text, default_val, command):
        sw = ctk.CTkSwitch(
            parent,
            text=text,
            font=ctk.CTkFont(size=12),
            progress_color="#00e5ff",
            command=command
        )
        if default_val:
            sw.select()
        else:
            sw.deselect()
        sw.pack(fill="x", padx=15, pady=6)
        return sw
        
    def _create_sound_picker(self, parent, key, current_path):
        frame = ctk.CTkFrame(parent, fg_color="#161b22", corner_radius=6)
        frame.pack(fill="x", padx=15, pady=(0, 10))
        
        name = Path(current_path).name if current_path else "None"
        lbl_file = ctk.CTkLabel(frame, text=f"📁 {name}", font=ctk.CTkFont(size=11), text_color="#c9d1d9", anchor="w")
        lbl_file.pack(side="left", fill="x", expand=True, padx=8, pady=4)
        
        # Test Play Button
        btn_play = ctk.CTkButton(
            frame,
            text="▶ Test",
            width=50,
            height=24,
            font=ctk.CTkFont(size=10),
            fg_color="#21262d",
            hover_color="#30363d",
            command=lambda: self._test_sound(key)
        )
        btn_play.pack(side="right", padx=(2, 6), pady=4)
        
        # Change Button
        btn_change = ctk.CTkButton(
            frame,
            text="Browse...",
            width=65,
            height=24,
            font=ctk.CTkFont(size=10),
            fg_color="#1f6feb",
            hover_color="#388bfd",
            command=lambda: self._browse_sound(key, lbl_file)
        )
        btn_change.pack(side="right", padx=2, pady=4)
        
        return {"label": lbl_file, "path": current_path}
        
    def _create_slider_control(self, parent, title, from_, to_, default_val, fmt, command):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=15, pady=(8, 2))
        ctk.CTkLabel(row, text=title, font=ctk.CTkFont(size=12)).pack(side="left")
        lbl_val = ctk.CTkLabel(row, text=fmt % default_val, font=ctk.CTkFont(size=12, weight="bold"), text_color="#00e5ff")
        lbl_val.pack(side="right")
        
        slider = ctk.CTkSlider(parent, from_=from_, to=to_, number_of_steps=50, command=lambda v: command(v, lbl_val, fmt))
        slider.set(default_val)
        slider.pack(fill="x", padx=15, pady=(0, 6))
        return slider

    # =========================================================================
    # Audio & Sound Management Handlers
    # =========================================================================
    def _browse_sound(self, key, label_widget):
        file_path = filedialog.askopenfilename(
            title=f"Select Custom Audio for {key.capitalize()}",
            filetypes=[("Audio Files", "*.mp3 *.wav *.ogg *.flac"), ("All Files", "*.*")]
        )
        if file_path:
            p = Path(file_path)
            if key == "sleep":
                self.config.audio_sleep_path = p
            elif key == "phone":
                self.config.audio_phone_path = p
            elif key == "face_hidden":
                self.config.audio_face_hidden_path = p
                
            self.engine.audio_manager.load_sound(key, p)
            label_widget.configure(text=f"📁 {p.name}")
            
    def _test_sound(self, key):
        threading.Thread(target=self._play_preview_sound, args=(key,), daemon=True).start()
        
    def _play_preview_sound(self, key):
        try:
            if key in self.engine.audio_manager.sounds:
                snd = self.engine.audio_manager.sounds[key]
                snd.play()
                time.sleep(1.5)
                snd.stop()
        except Exception as e:
            print(f"Audio preview error: {e}")

    # =========================================================================
    # Toggle & Slider Event Callbacks
    # =========================================================================
    def _on_toggle_sleep_det(self):
        self.config.enable_sleep_detection = bool(self.sw_sleep_det.get())
        
    def _on_toggle_phone_det(self):
        self.config.enable_phone_detection = bool(self.sw_phone_det.get())
        
    def _on_toggle_abs_det(self):
        self.config.enable_absence_detection = bool(self.sw_abs_det.get())
        
    def _on_toggle_hud(self):
        self.config.show_hud = bool(self.sw_hud.get())
        
    def _on_toggle_master_audio(self):
        self.config.audio_muted = not bool(self.sw_master_audio.get())
        if self.config.audio_muted:
            self.engine.audio_manager.stop_all()
            
    def _on_toggle_sleep_snd(self):
        self.config.enable_sleep_audio = bool(self.sw_sleep_snd.get())
        if not self.config.enable_sleep_audio and self.engine.audio_manager.current_playing == "sleep":
            self.engine.audio_manager.stop_all()
            
    def _on_toggle_phone_snd(self):
        self.config.enable_phone_audio = bool(self.sw_phone_snd.get())
        if not self.config.enable_phone_audio and self.engine.audio_manager.current_playing == "phone":
            self.engine.audio_manager.stop_all()
            
    def _on_toggle_abs_snd(self):
        self.config.enable_absence_audio = bool(self.sw_abs_snd.get())
        if not self.config.enable_absence_audio and self.engine.audio_manager.current_playing == "face_hidden":
            self.engine.audio_manager.stop_all()
            
    def _on_vol_change(self, val):
        self.config.audio_volume = float(val)
        self.lbl_vol.configure(text=f"{int(val*100)}%")
        self.engine.audio_manager.set_volume(self.config.audio_volume)
        
    def _on_phone_conf_change(self, val, lbl, fmt):
        self.config.phone_confidence_threshold = float(val)
        lbl.configure(text=fmt % val)
        self.engine.object_detector.conf_threshold = self.config.phone_confidence_threshold
        
    def _on_pitch_thresh_change(self, val, lbl, fmt):
        self.config.reading_pitch_threshold = float(val)
        lbl.configure(text=fmt % val)
        
    def _on_camera_select(self, val):
        self.config.camera_index = int(val)
        if self.is_running:
            self.toggle_session() # Stop
            self.toggle_session() # Restart with new camera

    # =========================================================================
    # Session Execution Engine
    # =========================================================================
    def toggle_session(self):
        if not self.is_running:
            self.start_session()
        else:
            self.stop_session()
            
    def start_session(self):
        self.cap = cv2.VideoCapture(self.config.camera_index)
        if not self.cap.isOpened():
            messagebox.showerror("Camera Error", f"Could not open camera device #{self.config.camera_index}.")
            return
            
        self.is_running = True
        self.engine.start_session()
        self.btn_start.configure(
            text="⏹ Stop Sentinel Session", 
            fg_color="#d32f2f", 
            hover_color="#f44336"
        )
        self.status_badge.configure(text="● ACTIVE MONITORING", text_color="#00e676", fg_color="#003314")
        
        self.thread = threading.Thread(target=self._video_loop, daemon=True)
        self.thread.start()
        
    def stop_session(self):
        self.is_running = False
        if self.cap:
            self.cap.release()
            self.cap = None
            
        self.engine.stop_session()
        self.btn_start.configure(
            text="▶ Start Sentinel Session", 
            fg_color="#00c853", 
            hover_color="#00e676"
        )
        self.status_badge.configure(text="● STANDBY", text_color="#9ba1a6", fg_color="#1e232d")
        self.video_label.configure(image=None, text="Session stopped\nClick 'Start Sentinel Session' to resume")
        
    def reset_session(self):
        self.engine.metrics = self.engine.metrics.__class__()
        self.engine.metrics.start()
        self.card_focus.configure(text="100%")
        self.card_time.configure(text="00:00")
        self.card_distractions.configure(text="0")
        self.card_pitch.configure(text="0.0°")
        
    def _video_loop(self):
        while self.is_running and self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                break
                
            processed_frame, state, metrics = self.engine.process_frame(frame)
            
            # Convert BGR OpenCV image to RGB PIL Image for CustomTkinter UI
            rgb_frame = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
            h, w, _ = rgb_frame.shape
            
            # Responsive aspect scaling
            target_w = 640
            target_h = int(h * (target_w / w))
            resized = cv2.resize(rgb_frame, (target_w, target_h))
            img = Image.fromarray(resized)
            ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(target_w, target_h))
            
            # Update UI on main thread safely
            self.after(0, self._update_ui_frame, ctk_img, state, metrics)
            time.sleep(0.01)
            
    def _update_ui_frame(self, ctk_img, state: FocusState, metrics):
        if not self.is_running:
            return
            
        self.video_label.configure(image=ctk_img, text="")
        
        # Update Stats Cards
        self.card_focus.configure(text=f"{metrics.focus_score:.0f}%")
        mins, secs = divmod(int(metrics.total_focus_seconds), 60)
        self.card_time.configure(text=f"{mins:02d}:{secs:02d}")
        
        total_distract = metrics.sleep_events_count + metrics.phone_events_count + metrics.absence_events_count
        self.card_distractions.configure(text=str(total_distract))
        self.card_pitch.configure(text=f"{metrics.current_pitch:.1f}°")
        
        # Update Status Badge Color Based on Live State
        if state == FocusState.FOCUSED:
            self.status_badge.configure(text="● OPTIMAL FOCUS", text_color="#00e676", fg_color="#003314")
        elif state == FocusState.READING_OR_WRITING:
            self.status_badge.configure(text="● DESK / NOTE READING", text_color="#00e5ff", fg_color="#002b3d")
        elif state == FocusState.MICRO_SLEEP:
            self.status_badge.configure(text="⚠️ SLEEP / DROWSINESS", text_color="#ff5252", fg_color="#3d0c0c")
        elif state == FocusState.PHONE_DISTRACTION:
            self.status_badge.configure(text="⚠️ PHONE DISTRACTION", text_color="#ffab00", fg_color="#3d2800")
        elif state == FocusState.FACE_ABSENT:
            self.status_badge.configure(text="⚠️ USER ABSENT", text_color="#ff5252", fg_color="#3d0c0c")
            
    def _on_close(self):
        self.stop_session()
        self.destroy()
        sys.exit(0)

def launch_gui():
    app = FocusSentinelApp()
    app.mainloop()

if __name__ == "__main__":
    launch_gui()
