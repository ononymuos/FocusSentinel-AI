#!/usr/bin/env bash
# =============================================================================
# FocusSentinel AI - Linux One-Click Installer & Desktop Integration
# Author: Usama Baig (https://github.com/ononymuos/FocusSentinel-AI)
# =============================================================================
set -euo pipefail

APP_NAME="FocusSentinel AI"
APP_ID="focussentinel-ai"
INSTALL_DIR="${HOME}/.local/share/focussentinel-ai"
BIN_DIR="${HOME}/.local/bin"
DESKTOP_DIR="${HOME}/.local/share/applications"

echo "============================================================="
echo "  🛡️  Installing FocusSentinel AI for Linux"
echo "  Author: Usama Baig"
echo "============================================================="

# 1. Check Python & venv availability
if ! command -v python3 &>/dev/null; then
    echo "[!] Error: python3 is required. Please install python3 (e.g. sudo apt install python3 python3-venv)"
    exit 1
fi

# Check system audio / camera libraries on Debian/Ubuntu systems
if command -v apt-get &>/dev/null; then
    echo "[*] Note: If audio or video dependencies are missing, run:"
    echo "    sudo apt-get install -y libgl1 libglib2.0-0 libasound2-dev portaudio19-dev"
fi

# 2. Create destination directories
echo "[*] Creating application directories at: ${INSTALL_DIR}"
mkdir -p "${INSTALL_DIR}"
mkdir -p "${BIN_DIR}"
mkdir -p "${DESKTOP_DIR}"

# Copy project files
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cp -r "${SCRIPT_DIR}/assets" "${INSTALL_DIR}/"
cp -r "${SCRIPT_DIR}/focussentinel" "${INSTALL_DIR}/"
cp "${SCRIPT_DIR}/main.py" "${INSTALL_DIR}/"
cp "${SCRIPT_DIR}/requirements.txt" "${INSTALL_DIR}/"
cp "${SCRIPT_DIR}/icon.png" "${INSTALL_DIR}/" 2>/dev/null || true

# 3. Setup isolated virtual environment
echo "[*] Setting up dedicated Python virtual environment..."
python3 -m venv "${INSTALL_DIR}/.venv"
"${INSTALL_DIR}/.venv/bin/pip" install --upgrade pip setuptools wheel
"${INSTALL_DIR}/.venv/bin/pip" install -r "${INSTALL_DIR}/requirements.txt" customtkinter

# 4. Create launcher binary in ~/.local/bin
cat << 'EOF' > "${BIN_DIR}/focussentinel"
#!/usr/bin/env bash
INSTALL_DIR="${HOME}/.local/share/focussentinel-ai"
cd "${INSTALL_DIR}"
exec "${INSTALL_DIR}/.venv/bin/python" "${INSTALL_DIR}/main.py" "$@"
EOF
chmod +x "${BIN_DIR}/focussentinel"

# 5. Create standard XDG Desktop Entry (.desktop)
cat << EOF > "${DESKTOP_DIR}/${APP_ID}.desktop"
[Desktop Entry]
Version=1.0
Type=Application
Name=${APP_NAME}
Comment=Real-time Computer Vision Focus & Attention Monitor
Exec=${BIN_DIR}/focussentinel
Icon=${INSTALL_DIR}/icon.png
Terminal=false
Categories=Utility;Education;Science;
StartupNotify=true
StartupWMClass=focussentinel
EOF
chmod +x "${DESKTOP_DIR}/${APP_ID}.desktop"

# Update desktop database if tool is present
if command -v update-desktop-database &>/dev/null; then
    update-desktop-database "${DESKTOP_DIR}" 2>/dev/null || true
fi

# Create an uninstaller script
cat << 'EOF' > "${INSTALL_DIR}/uninstall.sh"
#!/usr/bin/env bash
set -e
echo "[*] Uninstalling FocusSentinel AI..."
rm -rf "${HOME}/.local/share/focussentinel-ai"
rm -f "${HOME}/.local/bin/focussentinel"
rm -f "${HOME}/.local/share/applications/focussentinel-ai.desktop"
echo "[✓] FocusSentinel AI has been successfully uninstalled."
EOF
chmod +x "${INSTALL_DIR}/uninstall.sh"

echo "============================================================="
echo "  ✅ Installation Complete!"
echo "  - Run from terminal: focussentinel"
echo "  - Or launch 'FocusSentinel AI' from your Linux App Launcher / Menu"
echo "  - To uninstall: ${INSTALL_DIR}/uninstall.sh"
echo "============================================================="
