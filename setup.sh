#!/bin/bash

# =======================================
# ThePhish Setup Script (Robust Version)
# =======================================
# Prepares the environment, installs dependencies,
# sets up MongoDB 4.4, and launches a virtualenv.
# For Ubuntu 20.04 (or similar).
# =======================================

set -e  # Exit on any command failure

# Define colors
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Enforce running with sudo
if [ "$EUID" -ne 0 ]; then
  echo -e "${RED}❌ Please run this script using: sudo bash setup.sh${NC}"
  exit 1
fi

# Check if we're in the right directory
if [ ! -d "app" ]; then
  echo -e "${RED}❌ 'app/' directory not found. Please run this script from the root of the cloned project.${NC}"
  exit 1
fi

# 1. Display header
echo -e "\n🔧 ${GREEN}Starting setup for ThePhish_POC_DBERT...${NC}"

# 2. Check internet connection
echo -e "\n🌐 Checking internet connectivity..."
if ping -q -c 1 google.com >/dev/null 2>&1; then
  echo -e "${GREEN}✅ Internet connection verified.${NC}"
else
  echo -e "${RED}❌ No internet connection. Please check your network.${NC}"
  exit 1
fi

# 3. Install system-level dependencies
echo -e "\n📦 Installing system packages..."
apt update && apt install -y \
  python3 \
  python3-pip \
  python3-venv \
  build-essential \
  git \
  libssl-dev \
  wget \
  gnupg

# 4. Install MongoDB 4.4 (if not already present)
echo -e "\n🗄️  Installing MongoDB 4.4..."
if [ ! -f /etc/apt/sources.list.d/mongodb-org-4.4.list ]; then
  wget -qO - https://www.mongodb.org/static/pgp/server-4.4.asc | apt-key add -
  echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/4.4 multiverse" | \
    tee /etc/apt/sources.list.d/mongodb-org-4.4.list
  apt update
fi
apt install -y mongodb-org
systemctl enable --now mongod

# 5. Python version check
PY_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:3])))')
echo -e "\n🐍 Detected Python version: ${GREEN}$PY_VERSION${NC}"

# 6. Create virtual environment
echo -e "\n📁 Creating virtual environment..."
python3 -m venv venv
. venv/bin/activate

# 7. Install Python dependencies
echo -e "\n📦 Installing Python packages from requirements..."
pip install --upgrade pip
pip install -r app/requirements.txt

if [ -f "app/requirements-ml.txt" ]; then
  echo -e "\n🧠 Installing ML model dependencies..."
  pip install -r app/requirements-ml.txt
else
  echo -e "${RED}⚠️  app/requirements-ml.txt not found. ML functionality may be limited.${NC}"
fi

# 8. Completion message
echo -e "\n✅ ${GREEN}Setup complete!${NC}"
echo -e "To run ThePhish:\n"
echo "  . venv/bin/activate"
echo "  cd app"
echo "  python3 thephish_app.py"
echo -e "\n📌 ${RED}Don't forget:${NC} Configure your email credentials in 'app/.env' or 'app/configuration.json'."
echo -e "📂 Place your fine-tuned model in 'app/distilbert_phishing_finetuned_best/'"

