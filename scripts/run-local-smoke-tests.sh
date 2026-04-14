#!/usr/bin/env bash

set -euo pipefail

uv run pytest \
    tests/test_character.py \
    tests/test_readers.py \
    tests/test_magic_items.py \
    tests/test_armor_yaml.py \
    tests/test_weapons_yaml.py \
    tests/test_latex.py