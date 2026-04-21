#!/bin/bash
# =====================================================
# Setup script for Hand Gesture Recognition System
# Jetson Orin NX — Ubuntu 20.04 / JetPack 5.x
# =====================================================

# Cytron ASCII Art
echo "  __   ____      _                    __  "
echo " / /  / ___|   _| |_ _ __ ___  _ __   \ \ "
echo "| |  | |  | | | | __| '__/ _ \| '_ \   | |"
echo "| |  | |__| |_| | |_| | | (_) | | | |  | |"
echo "| |   \____\__, |\__|_|  \___/|_| |_|  | |"
echo " \_\       |___/                      /_/ "

set -e  # Exit on error

echo "============================================="
echo " Hand Gesture Recognition System Setup"
echo " Jetson Orin NX"
echo "============================================="

# ── 1. Update system ──────────────────────────────
echo "[1/6] Updating package list..."
sudo apt-get update -qq

# ── 2. Install system dependencies ────────────────
echo "[2/6] Installing system dependencies..."
sudo apt-get install -y \
    python3-pip \
    python3-dev \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgl1-mesa-glx \
    xdotool \
    v4l-utils

# ── 3. Check for available USB cameras ─────────────
echo "[3/6] Checking available USB cameras..."
v4l2-ctl --list-devices 2>/dev/null || echo "  (No camera detected, please connect a USB webcam)"

# ── 4. Install/Upgrade numpy ───────────────────────
echo "[4/6] Installing/Upgrading numpy..."
pip install --upgrade numpy -q

# ── 5. Install Python packages ─────────────────────
echo "[5/6] Installing Python packages..."
pip install --upgrade pip -q

# Install OpenCV (Jetson version for better performance)
pip install opencv-python -q

# Install MediaPipe
pip install mediapipe -q

# Install Streamlit and other dependencies from requirements.txt
pip install -r requirements.txt -q

echo "[6/6] Setup completed!"
echo ""
echo "============================================="
echo " How to run the application:"
echo ""
echo "   source venv/bin/activate"
echo "   streamlit run app.py --server.port 8501"
echo ""
echo " Then open a web browser:"
echo "   http://localhost:8501"
echo "============================================="
