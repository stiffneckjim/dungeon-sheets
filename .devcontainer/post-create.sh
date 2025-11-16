#!/bin/bash
set -ex

echo "Initializing development environment..."

# Initialize git submodules
git submodule update --init --recursive

# Install dungeon-sheets in editable mode with dev dependencies
pip install -e ".[dev]"

echo "Development environment ready!"
