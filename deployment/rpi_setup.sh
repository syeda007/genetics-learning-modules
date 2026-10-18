#!/bin/bash
# ==============================================================================
# Raspberry Pi 3 Deployment & Environment Setup Script
# Advanced Interactive Genetics Research and Experimentation System
# Target OS: Raspberry Pi OS (32-bit or 64-bit) with Desktop Environment
# Display: 7-inch HDMI Display (800x480 / 1024x600)
# ==============================================================================

set -e

echo "=== [1/5] Updating APT Repositories ==="
sudo apt-get update

echo "=== [2/5] Installing System Prerequisites & Qt5 Libraries ==="
sudo apt-get install -y python3 python3-pip python3-venv \
    python3-pyqt5 python3-pyqt5.qtquick libqt5gui5 \
    python3-numpy python3-scipy python3-gpiozero python3-rpi.gpio

echo "=== [3/5] Setting up Isolated Python Virtual Environment with System Site Packages ==="
cd "$(dirname "$0")/.."
python3 -m venv --system-site-packages .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "=== [4/5] Setting Safe GPIO Permissions (Non-root user) ==="
sudo usermod -a -G gpio,spi,i2c $USER

echo "=== [5/5] Configuring 7-inch HDMI Display (1024x600 / 800x480) ==="
# Append optimal HDMI timings for 7-inch displays to /boot/config.txt if not present
if ! grep -q "hdmi_cvt 1024 600" /boot/config.txt 2>/dev/null; then
    echo "# Recommended 7-inch HDMI Display Timings" | sudo tee -a /boot/config.txt
    echo "hdmi_group=2" | sudo tee -a /boot/config.txt
    echo "hdmi_mode=87" | sudo tee -a /boot/config.txt
    echo "hdmi_cvt 1024 600 60 6 0 0 0" | sudo tee -a /boot/config.txt
    echo "hdmi_drive=1" | sudo tee -a /boot/config.txt
fi

echo "=== Raspberry Pi Deployment Setup Complete ==="
echo "Launch with: ./run_app.sh or python3 main.py"
