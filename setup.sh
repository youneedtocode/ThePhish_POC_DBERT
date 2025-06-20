#!/bin/bash

# =======================================
# ThePhish Setup Script
# =======================================
# Sets up Python environment,
# installs required system and Python packages,
# and prepares ThePhish for local execution.
# =======================================

set -e  # Exit on any error

# 1. Display header
echo "\n🔧 Starting setup for ThePhish_POC_DBERT..."

# 2. Install system-level dependencies (Debian/Ubuntu based systems)
echo "\n📦 Installing system dependencies..."
sudo apt update && sudo apt install -y \
  python3 \
  python3-pip \
  python3-venv \
  build-essential \
  git \
  libssl-dev

# 3. Python version check
PY_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:3])))')
echo "\n🐍 Detected Python version: $PY_VERSION"

# 4. Create virtual environment
echo "\n📁 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# 5. Upgrade pip and install Python dependencies
echo "\n📦 Installing Python packages from requirements.txt..."
pip install --upgrade pip
pip install -r app/requirements.txt

# 6. Install additional ML dependencies
if [ -f "app/requirements-ml.txt" ]; then
  echo "\n🧠 Installing ML model dependencies from requirements-ml.txt..."
  pip install -r app/requirements-ml.txt
else
  echo "⚠️  'app/requirements-ml.txt' not found. ML model support will be incomplete."
fi

# 7. Final message
echo "\n✅ Setup complete."
echo "To run ThePhish, do the following:"
echo "----------------------------------------"
echo "source venv/bin/activate"
echo "cd app"
echo "python3 thephish_app.py"
echo "----------------------------------------"
echo "\n📌 Don't forget to configure 'app/.env' and place your model directory in 'app/'."
