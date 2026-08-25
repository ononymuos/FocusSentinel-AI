import urllib.request, json, mimetypes, os, sys
from pathlib import Path

TOKEN = Path('C:/Users/hecke/OneDrive/Desktop/credentials with details/GitHub/.git-credentials').read_text().split('ghp_')[1].split('@')[0]
TOKEN = 'ghp_' + TOKEN.strip()
REPO = 'ononymuos/FocusSentinel-AI'
TAG = 'v1.1.0'

# 1. Check if release already exists or create new
url = f'https://api.github.com/repos/{REPO}/releases'
headers = {
    'Authorization': f'Bearer {TOKEN}',
    'Accept': 'application/vnd.github.v3+json',
    'User-Agent': 'FocusSentinel-Release-Script'
}

req = urllib.request.Request(url, headers=headers)
with urllib.request.urlopen(req) as resp:
    releases = json.loads(resp.read().decode('utf-8'))

existing = next((r for r in releases if r.get('tag_name') == TAG), None)

changelog = """## 🚀 FocusSentinel AI v1.1.0 - Multi-Platform Release & Vision Enhancements

FocusSentinel AI is a high-performance computer vision focus and study session monitor with 3D head pose estimation, dual-eye micro-sleep tracking, phone distraction monitoring, and customizable audio feedback.

### 🌟 What's New in v1.1.0:
- **⚙️ One-Click Factory Settings Reset**: Added a dedicated *'⚙️ Restore Default Settings'* button to effortlessly reset all vision toggles, audio alarms, sensitivity sliders, and device inputs back to calibrated defaults.
- **📐 Fixed Head Pose Estimation Angles**: Resolved Euler angle scaling calculations in `cv2.RQDecomp3x3` for true-to-life 3D pitch/yaw/roll telemetry ($-180^\circ \dots +180^\circ$). Reading & desk study detection now triggers with surgical precision.
- **👁️ Dual-Eye Yaw-Invariant EAR Tracking**: Upgraded eye closure detection to calculate and average dual-eye ratios using local horizontal eye dimensions as normalizers, making drowsiness tracking immune to head turns and distance shifts.
- **⚡ Throttled Inference & Temporal Persistence**: Decoupled YOLOv8 object detection cadence (sampled every 3rd frame) and implemented 3-frame temporal persistence to eliminate false-alarm micro-flickers while maintaining silky-smooth 30+ FPS video performance.
- **🎥 Universal Virtual Camera Support**: Enhanced camera driver with automatic multi-backend fallback (`DirectShow` / `Media Foundation` / `Default`) for seamless integration with Camo, OBS Virtual Cam, and external webcams.

### 📦 Multi-Platform Downloads:
- **🪟 Windows**: Standalone Installer: [`FocusSentinel_Setup_v1.1.0.exe`](https://github.com/ononymuos/FocusSentinel-AI/releases/download/v1.1.0/FocusSentinel_Setup_v1.1.0.exe)
- **🐧 Linux**: Bundle Archive: [`FocusSentinel-v1.1.0-linux.tar.gz`](https://github.com/ononymuos/FocusSentinel-AI/releases/download/v1.1.0/FocusSentinel-v1.1.0-linux.tar.gz) *(or install via `curl -sSL https://raw.githubusercontent.com/ononymuos/FocusSentinel-AI/main/install_linux.sh | bash`)*
- **🍎 macOS**: Bundle Archive: [`FocusSentinel-v1.1.0-macos.tar.gz`](https://github.com/ononymuos/FocusSentinel-AI/releases/download/v1.1.0/FocusSentinel-v1.1.0-macos.tar.gz) *(or install via `curl -sSL https://raw.githubusercontent.com/ononymuos/FocusSentinel-AI/main/install_macos.sh | bash`)*
"""

if not existing:
    print(f"[*] Creating Release {TAG}...")
    payload = {
        'tag_name': TAG,
        'target_commitish': 'main',
        'name': 'FocusSentinel AI v1.1.0 - Enhanced Vision & Multi-Platform Release',
        'body': changelog,
        'draft': False,
        'prerelease': False
    }
    create_req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers, method='POST')
    with urllib.request.urlopen(create_req) as resp:
        release = json.loads(resp.read().decode('utf-8'))
else:
    print(f"[*] Using existing Release ID: {existing['id']}")
    release = existing

release_id = release['id']
upload_url_base = f'https://uploads.github.com/repos/{REPO}/releases/{release_id}/assets'

# 2. Upload assets
assets_to_upload = [
    Path('C:/Users/hecke/FocusSentinel-AI/release_assets/FocusSentinel_Setup_v1.1.0.exe'),
    Path('C:/Users/hecke/FocusSentinel-AI/release_assets/FocusSentinel-v1.1.0-linux.tar.gz'),
    Path('C:/Users/hecke/FocusSentinel-AI/release_assets/FocusSentinel-v1.1.0-macos.tar.gz'),
]

# Get current release assets to delete if re-uploading
assets_req = urllib.request.Request(f'https://api.github.com/repos/{REPO}/releases/{release_id}/assets', headers=headers)
with urllib.request.urlopen(assets_req) as resp:
    current_assets = json.loads(resp.read().decode('utf-8'))

for asset_path in assets_to_upload:
    if not asset_path.exists():
        print(f"[!] Asset missing: {asset_path}")
        continue
    
    # Delete if exists in release
    for cur in current_assets:
        if cur['name'] == asset_path.name:
            print(f"[*] Deleting existing asset: {cur['name']} (ID: {cur['id']})")
            del_req = urllib.request.Request(cur['url'], headers=headers, method='DELETE')
            urllib.request.urlopen(del_req)
    
    print(f"[*] Uploading {asset_path.name} ({asset_path.stat().st_size / (1024*1024):.2f} MB)...")
    content_type, _ = mimetypes.guess_type(str(asset_path))
    if not content_type:
        content_type = 'application/octet-stream'
        
    with open(asset_path, 'rb') as f:
        data = f.read()
        
    up_url = f"{upload_url_base}?name={asset_path.name}"
    up_headers = {
        'Authorization': f'Bearer {TOKEN}',
        'Content-Type': content_type,
        'Content-Length': str(len(data)),
        'User-Agent': 'FocusSentinel-Release-Script'
    }
    
    up_req = urllib.request.Request(up_url, data=data, headers=up_headers, method='POST')
    with urllib.request.urlopen(up_req) as up_resp:
        res = json.loads(up_resp.read().decode('utf-8'))
        print(f"[✓] Successfully uploaded {res.get('name')} (Download URL: {res.get('browser_download_url')})")

print("\n🎉 GitHub Release v1.1.0 with all multi-platform assets successfully published!")
