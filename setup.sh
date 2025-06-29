# =======================================
# ThePhish Setup Script
# =======================================
# Sets up Python environment,
# installs required system and Python packages,
# installs MongoDB 4.4,
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
  libssl-dev \
  wget \
  gnupg

# 3. Install MongoDB 4.4 from official repository
echo "\n🗄️  Installing MongoDB 4.4..."
wget -qO - https://www.mongodb.org/static/pgp/server-4.4.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/4.4 multiverse" | \
  sudo tee /etc/apt/sources.list.d/mongodb-org-4.4.list
sudo apt update
sudo apt install -y mongodb-org
sudo systemctl enable --now mongod

# 4. Python version check
PY_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:3])))')
echo "\n🐍 Detected Python version: $PY_VERSION"

# 5. Create virtual environment
echo "\n📁 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# 6. Upgrade pip and install Python dependencies
echo "\n📦 Installing Python packages from requirements.txt..."
pip install --upgrade pip
pip install -r app/requirements.txt

# 7. Install additional ML dependencies
if [ -f "app/requirements-ml.txt" ]; then
  echo "\n🧠 Installing ML model dependencies from requirements-ml.txt..."
  pip install -r app/requirements-ml.txt
else
  echo "⚠️  'app/requirements-ml.txt' not found. ML model support will be incomplete."
fi

# 8. Final message
echo "\n✅ Setup complete."
echo "To run ThePhish, do the following:"
echo "----------------------------------------"
echo "source venv/bin/activate"
echo "cd app"
echo "python3 thephish_app.py"
echo "----------------------------------------"
echo "\n📌 Don't forget to configure 'app/.env' and place your model directory in 'app/'."

