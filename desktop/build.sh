#!/bin/bash
set -e

echo "📦 Packaging Mami AI Desktop Client..."

# Install PyInstaller
pip install -r requirements.txt

# Create Executable
pyinstaller --noconfirm --onefile --console --name "MamiAI_Client" \
    --hidden-import="websocket" \
    --hidden-import="rich" \
    --collect-all="rich" \
    desktop/main.py

echo "✅ Build Complete! Executable is in 'dist/MamiAI_Client'"
