#!/data/data/com.termux/files/usr/bin/bash
set -e

echo "[NeforOS] Updating Termux packages..."
pkg update -y
pkg upgrade -y
pkg install -y python git

echo "[NeforOS] Installing Python dependencies..."
python -m pip install --upgrade pip
pip install -r requirements.txt

echo "[NeforOS] Installation complete."
echo "[NeforOS] Run ./start.sh to launch NeforOS"
