import urllib.request, json, mimetypes, os, sys
from pathlib import Path

TOKEN = Path('C:/Users/hecke/OneDrive/Desktop/credentials with details/GitHub/.git-credentials').read_text().split('ghp_')[1].split('@')[0]
TOKEN = 'ghp_' + TOKEN.strip()
REPO = 'ononymuos/FocusSentinel-AI'
TAG = 'v1.0.0'

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

changelog = """## 🚀 FocusSentinel AI v1.0.0 - Official Multi-Platform Release

FocusSentinel AI is a modern computer vision focus and study session monitor with 3D head pose estimation, micro-sleep detection, phone distraction tracking, and custom audio feedback.

### ✨ What's New:
- **🖥️ In-App Control Center GUI**: Modern CustomTkinter interface with live camera feed, real-time Focus Score %, and 3D head telemetry.
- **🔄 Detection Feature Toggles**: Individual on/off switches for Sleep Tracking, YOLOv8 Phone Detection, Absence Tracking, and HUD Overlay.
- **🎵 Custom Audio Alarms**: Full GUI sound file pickers for Sleep, Phone, and Absence alerts with live `▶ Test` audio preview buttons.
- **🎚️ Master Sound & Volume Control**: Integrated master mute switch and volume slider.
- **📦 Multi-Platform Native Installers**: Standalone installers and scripts for Windows, Linux, and macOS.

### 📥 Quick Install Instructions:
- **Windows**: Download and run `FocusSentinel_Setup_v1.0.0.exe`
- **Linux**: `curl -sSL https://raw.githubusercontent.com/ononymuos/FocusSentinel-AI/main/install_linux.sh | bash`
- **macOS**: `curl -sSL https://raw.githubusercontent.com/ononymuos/FocusSentinel-AI/main/install_macos.sh | bash`
"""

if not existing:
    print(f"[*] Creating Release {TAG}...")
    payload = {
        'tag_name': TAG,
        'target_commitish': 'main',
        'name': 'FocusSentinel AI v1.0.0 - Official Release',
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
    Path('C:/Users/hecke/FocusSentinel-AI/release_assets/FocusSentinel_Setup_v1.0.0.exe'),
    Path('C:/Users/hecke/FocusSentinel-AI/release_assets/FocusSentinel-v1.0.0-linux.tar.gz'),
    Path('C:/Users/hecke/FocusSentinel-AI/release_assets/FocusSentinel-v1.0.0-macos.tar.gz'),
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
    content_type = mimetypes.guess_type(str(asset_path))[0] or 'application/octet-stream'
    upload_headers = headers.copy()
    upload_headers['Content-Type'] = content_type
    
    upload_url = f"{upload_url_base}?name={asset_path.name}"
    with open(asset_path, 'rb') as f:
        data = f.read()
        
    up_req = urllib.request.Request(upload_url, data=data, headers=upload_headers, method='POST')
    with urllib.request.urlopen(up_req) as resp:
        result = json.loads(resp.read().decode('utf-8'))
        print(f"[✓] Successfully uploaded: {result['name']} -> {result['browser_download_url']}")

print("\n✅ ALL RELEASE ASSETS PUBLISHED TO GITHUB!")
