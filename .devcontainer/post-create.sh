#!/bin/zsh
echo "Installing dungeon-sheets development dependencies..."

# Initialize git submodules
echo "Initializing development environment..."

# If submodule init fails due to missing commits, try remote update
if ! git submodule update --init --recursive; then
    echo "Standard submodule update failed, trying remote update..."
    git submodule update --init --recursive --remote
fi

# Install dungeon-sheets in editable mode with dev dependencies
pip install -e ".[dev]"

echo "Development environment ready!"

# Sort zsh config
echo "Move zsh config"
cp /workspaces/dungeon-sheets/.devcontainer/.zshrc /home/vscode/.zshrc
# source /home/vscode/.zshrc
