#!/usr/bin/env bash
# =============================================================================
# FocusSentinel AI - macOS One-Click Installer & App Setup
# Author: Usama Baig (https://github.com/ononymuos/FocusSentinel-AI)
# =============================================================================
set -euo pipefail

APP_NAME="FocusSentinel AI"
APP_ID="focussentinel-ai"
INSTALL_DIR="${HOME}/.local/share/focussentinel-ai"
BIN_DIR="${HOME}/.local/bin"
APPLICATIONS_DIR="${HOME}/Applications"

echo "============================================================="
echo "  🛡️  Installing FocusSentinel AI for macOS"
echo "  Author: Usama Baig"
echo "============================================================="

# 1. Check Python 3
if ! command -v python3 &>/dev/null; then
    echo "[!] Error: python3 is required. Install via Homebrew: brew install python python-tk"
    exit 1
fi

# 2. Setup installation directories
echo "[*] Setting up application directory: ${INSTALL_DIR}"
mkdir -p "${INSTALL_DIR}"
mkdir -p "${BIN_DIR}"
mkdir -p "${APPLICATIONS_DIR}"

# Copy project files
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cp -r "${SCRIPT_DIR}/assets" "${INSTALL_DIR}/"
cp -r "${SCRIPT_DIR}/focussentinel" "${INSTALL_DIR}/"
cp "${SCRIPT_DIR}/main.py" "${INSTALL_DIR}/"
cp "${SCRIPT_DIR}/requirements.txt" "${INSTALL_DIR}/"
cp "${SCRIPT_DIR}/icon.png" "${INSTALL_DIR}/" 2>/dev/null || true

# 3. Create isolated Python environment
echo "[*] Creating dedicated virtual environment..."
python3 -m venv "${INSTALL_DIR}/.venv"
"${INSTALL_DIR}/.venv/bin/pip" install --upgrade pip setuptools wheel
"${INSTALL_DIR}/.venv/bin/pip" install -r "${INSTALL_DIR}/requirements.txt" customtkinter

# 4. Create launcher script
cat << 'EOF' > "${BIN_DIR}/focussentinel"
#!/usr/bin/env bash
INSTALL_DIR="${HOME}/.local/share/focussentinel-ai"
cd "${INSTALL_DIR}"
exec "${INSTALL_DIR}/.venv/bin/python3" "${INSTALL_DIR}/main.py" "$@"
EOF
chmod +x "${BIN_DIR}/focussentinel"

# 5. Create macOS .app bundle wrapper in ~/Applications
APP_BUNDLE="${APPLICATIONS_DIR}/FocusSentinel AI.app"
mkdir -p "${APP_BUNDLE}/Contents/MacOS"
mkdir -p "${APP_BUNDLE}/Contents/Resources"

cat << EOF > "${APP_BUNDLE}/Contents/MacOS/FocusSentinel"
#!/usr/bin/env bash
exec "${BIN_DIR}/focussentinel"
EOF
chmod +x "${APP_BUNDLE}/Contents/MacOS/FocusSentinel"

cat << EOF > "${APP_BUNDLE}/Contents/Info.plist"
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>FocusSentinel</string>
    <key>CFBundleIdentifier</key>
    <string>com.ononymuos.focussentinel</string>
    <key>CFBundleName</key>
    <string>${APP_NAME}</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0.0</string>
    <key>NSCameraUsageDescription</key>
    <string>FocusSentinel AI requires camera access for focus and attention monitoring.</string>
    <key>NSMicrophoneUsageDescription</key>
    <string>FocusSentinel AI alert audio system.</string>
</dict>
</plist>
EOF

# 6. Create Uninstaller
cat << 'EOF' > "${INSTALL_DIR}/uninstall.sh"
#!/usr/bin/env bash
set -e
echo "[*] Uninstalling FocusSentinel AI..."
rm -rf "${HOME}/.local/share/focussentinel-ai"
rm -f "${HOME}/.local/bin/focussentinel"
rm -rf "${HOME}/Applications/FocusSentinel AI.app"
echo "[✓] FocusSentinel AI successfully uninstalled."
EOF
chmod +x "${INSTALL_DIR}/uninstall.sh"

echo "============================================================="
echo "  ✅ macOS Installation Complete!"
echo "  - Run from Terminal: ~/.local/bin/focussentinel"
echo "  - Or launch 'FocusSentinel AI' from ~/Applications or Spotlight"
echo "  - To uninstall: ${INSTALL_DIR}/uninstall.sh"
echo "============================================================="
