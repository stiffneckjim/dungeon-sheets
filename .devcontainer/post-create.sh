#!/bin/bash
set -ex

echo "Installing dungeon-sheets development dependencies..."

# Initialize git submodules
echo "Initializing git submodules..."
git submodule update --init --recursive

# Install Python package in editable mode with dev dependencies
pip install -e ".[dev]"

# Install Kalam fonts for MSavage template
echo "Installing Kalam font..."
sudo mkdir -p /usr/share/fonts/truetype/kalam
cd /tmp
wget -q https://github.com/google/fonts/raw/main/ofl/kalam/Kalam-Regular.ttf
wget -q https://github.com/google/fonts/raw/main/ofl/kalam/Kalam-Bold.ttf
wget -q https://github.com/google/fonts/raw/main/ofl/kalam/Kalam-Light.ttf
sudo mv Kalam-*.ttf /usr/share/fonts/truetype/kalam/
sudo fc-cache -fv

# Install required LaTeX packages
echo "Installing LaTeX packages..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PACKAGES=$(bash "$SCRIPT_DIR/install-texlive-packages.sh")
sudo /usr/local/texlive/bin/x86_64-linux/tlmgr install $PACKAGES

echo "Setup complete!"
