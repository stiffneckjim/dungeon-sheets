# AI Agent Instructions for dungeon-sheets

This document guides AI coding agents on effectively working with the dungeon-sheets codebase, a tool for creating D&D 5e character sheets and session notes.

## Project Overview

dungeon-sheets is a Python package that:

- Generates character sheets and GM notes for D&D 5th Edition
- Supports multiple output formats (PDF, ePub)
- Handles character data from Python files and VTT JSON exports
- Requires Python 3.9+ and uses modern Python features

## Core Architecture

The project follows a modular architecture with these key components:

1. **Character Model** (`dungeonsheets/character.py`):

   - Base `Character` class that other classes inherit from
   - Handles core character attributes, calculated stats, and feature management

2. **Content System** (`dungeonsheets/content_registry.py`, `dungeonsheets/content.py`):

   - Registry pattern for D&D content (spells, items, features)
   - Use `content_registry.register_X()` for adding new content

3. **Output Generation** (`dungeonsheets/make_sheets.py`):
   - Entry point for sheet generation via `makesheets` command
   - Supports PDF (via pdftk/pypdf) and ePub formats

## Key Workflows

### Testing

```bash
pip install -e ".[dev]"  # Install dev dependencies
pytest tests/            # Run test suite
pytest tests/ -k test_name  # Run specific test
```

### Development Setup

```bash
pip install -e "."      # Install in editable mode
sudo apt-get -y install pdftk texlive-latex-base texlive-latex-extra texlive-fonts-recommended  # Optional: PDF dependencies
```

## Project Conventions

1. **Class Creation**:

   - Character classes (Fighter, Wizard, etc.) inherit from `Character`
   - New features should be registered via `content_registry`
   - Example: See `dungeonsheets/classes/wizard.py`

2. **Testing**:

   - Tests are organized by component in `tests/`
   - Use `TestCase` for test classes
   - Mock external dependencies (pdftk, latex)

3. **Content Addition**:

   ```python
   from dungeonsheets.content_registry import register_spell

   @register_spell
   class NewSpell:
       """Follow existing spell pattern"""
       pass
   ```

## Integration Points

1. **PDF Generation**:

   - Primary: pdftk for form filling
   - Fallback: pypdf library
   - LaTeX for spell pages (optional)

2. **Data Import**:
   - Python character files (primary)
   - VTT JSON exports (supported formats in `dungeonsheets/readers.py`)

## Common Pitfalls

1. **PDF Generation**: Always check `pdftk` availability before using PDF-specific features
2. **Python Files**: Character files require exact class/feature names matching registry
3. **Dependencies**: Some features need external tools (pdftk, latex) - handle gracefully

## Example Files

Check these files to understand common patterns:

- Basic character: `examples/wizard1.py`
- Complex character: `examples/multiclass1.py`
- GM notes: `examples/gm-campaign-notes.py`
- Test patterns: `tests/test_character.py`
