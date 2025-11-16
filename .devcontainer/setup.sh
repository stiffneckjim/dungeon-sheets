#!/bin/bash
set -e  # Exit on error
set -x  # Print commands as they execute

echo "Installing dungeon-sheets development dependencies..."

# Initialize git submodules
echo "Initializing git submodules..."
git submodule update --init --recursive

# Install system dependencies
sudo apt-get update
sudo apt-get install -y --no-install-recommends \
    pdftk-java \
    wget \
    perl \
    fontconfig

# Install Python package in editable mode with dev dependencies
pip install -e ".[dev]"

# Install minimal TeX Live
echo "Installing minimal TeX Live..."
cd /tmp
echo "Downloading TeX Live installer..."
wget --timeout=60 --tries=3 -q https://mirror.ctan.org/systems/texlive/tlnet/install-tl-unx.tar.gz || {
    echo "Failed to download TeX Live installer"
    exit 1
}
echo "Extracting installer..."
tar -xzf install-tl-unx.tar.gz
cd install-tl-*/

# Create minimal profile
cat > texlive.profile << 'EOF'
selected_scheme scheme-basic
TEXDIR /usr/local/texlive
TEXMFLOCAL /usr/local/texlive/texmf-local
TEXMFSYSVAR /usr/local/texlive/texmf-var
TEXMFSYSCONFIG /usr/local/texlive/texmf-config
TEXMFVAR ~/.texlive/texmf-var
TEXMFCONFIG ~/.texlive/texmf-config
TEXMFHOME ~/texmf
option_doc 0
option_src 0
instopt_adjustpath 1
EOF

# Install TeX Live
echo "Running TeX Live installer (this may take a few minutes)..."
sudo perl ./install-tl --profile=texlive.profile --no-interaction || {
    echo "TeX Live installation failed"
    exit 1
}

# Add to PATH for current shell
export PATH="/usr/local/texlive/bin/x86_64-linux:$PATH"

# Add to /etc/profile.d for login shells
echo 'export PATH="/usr/local/texlive/bin/x86_64-linux:$PATH"' | sudo tee /etc/profile.d/texlive.sh

# Add to vscode user's .bashrc for non-login shells (VS Code terminals)
echo 'export PATH="/usr/local/texlive/bin/x86_64-linux:$PATH"' >> ~/.bashrc

# Install Kalam font for MSavage template
echo "Installing Kalam font..."
sudo mkdir -p /usr/share/fonts/truetype/kalam
cd /tmp
wget -q https://github.com/google/fonts/raw/main/ofl/kalam/Kalam-Regular.ttf
wget -q https://github.com/google/fonts/raw/main/ofl/kalam/Kalam-Bold.ttf
wget -q https://github.com/google/fonts/raw/main/ofl/kalam/Kalam-Light.ttf
sudo mv Kalam-*.ttf /usr/share/fonts/truetype/kalam/

# Install required LaTeX packages
echo "Installing LaTeX packages..."
# Get the script directory - works both when run directly and via postCreateCommand
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PACKAGES=$(bash "$SCRIPT_DIR/install-texlive-packages.sh")
sudo /usr/local/texlive/bin/x86_64-linux/tlmgr install $PACKAGES

# Update font cache
sudo fc-cache -fv

# Clean up
cd /
sudo rm -rf /tmp/install-tl-*

echo "Setup complete! TeX Live and dependencies installed."
echo "Run 'source /etc/profile.d/texlive.sh' to update PATH in current shell."
