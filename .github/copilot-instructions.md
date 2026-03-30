# AI Agent Instructions for dungeon-sheets

dungeon-sheets is a Python package (3.10+) that generates D&D 5e character sheets and GM notes in PDF/ePub formats. Character data is defined in Python files or imported from VTT JSON exports.

## Build, Test & Lint Commands

Uses **`uv`** for package management — never use `pip` directly.

```bash
uv sync --all-extras        # Install all dependencies (including dev)
```

```bash
uv run pytest tests/        # Full test suite
uv run pytest tests/test_character.py::TestCharacter::test_max_hp  # Single test
uv run pytest tests/ -k "test_spell_slots"  # Filter by name
```

```bash
uv run ruff check dungeonsheets/           # Lint
uv run ruff format --check dungeonsheets/  # Format check
uv run ruff format dungeonsheets/          # Apply formatting
```

Line length is **100 characters** (configured in `pyproject.toml`).

System dependencies required for PDF output: `pdftk` and a working `pdflatex`. The exact provisioning steps differ from a simple `apt-get` install — CI installs TeX Live via the upstream installer and `tlmgr`. See the [workflow file](.github/workflows/python-ci.yml) and [Dockerfile](Dockerfile) for the precise install steps used in CI/Docker.

Tests use `unittest.TestCase` but are discovered and run via `pytest`.

## Development Workflow (GitHub Flow)

This project follows the **GitHub Flow** model. All changes must be made on a feature branch before raising a pull request:

1. **Create a Feature Branch**:

   ```bash
   # Ensure you're on main and up to date
   git checkout main
   git pull origin main

   # Create a new branch with a descriptive name
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/bug-description
   # or
   git checkout -b perf/performance-improvement
   ```

2. **Make Changes**:

   - Implement your feature or fix
   - Write/update tests as needed
   - Ensure all tests pass locally

3. **Commit and Push**:

   ```bash
   git add .
   git commit -m "Descriptive commit message"
   # First push of a new branch - set upstream
   git push -u origin feature/your-feature-name
   # Subsequent pushes
   git push
   ```

4. **Create Pull Request**:

   - Set default repository for GitHub CLI (first time only):
     ```bash
     gh repo set-default stiffneckjim/dungeon-sheets
     ```
   - Open a PR from your branch to `main`:
     ```bash
     gh pr create --title "Your PR title" --body "PR description" --base main
     ```
   - CI/CD workflows will automatically run
   - Address any review feedback

5. **Branch Naming Conventions**:
   - `feature/` - New features or enhancements
   - `fix/` - Bug fixes
   - `perf/` - Performance improvements
   - `docs/` - Documentation updates
   - `refactor/` - Code refactoring

**Never commit directly to `main`**. Always work on a feature branch and use pull requests for code review and CI validation.

## Architecture

### Data Flow

```
Character File (.py or .json)
    ↓ readers.read_sheet_file()
dict of character properties
    ↓ Character.load()
Character instance
    ↓ set_attrs() → _resolve_mechanic()
Strings resolved to classes (e.g., "shortsword" → Shortsword)
    ↓ CharacterRenderer (Jinja2)
LaTeX / HTML rendered from forms/ templates
    ↓ pdftk / pypdf / pdflatex
PDF or ePub output
```

### Key Modules

| Module | Role |
|--------|------|
| `character.py` | `Character` class + multiclass logic, computed properties (spell slots, AC, proficiency bonus) |
| `content_registry.py` | `ContentRegistry` singleton; resolves string names to Python classes |
| `content.py` | `Content` and `Creature` base classes; `_resolve_mechanic()` for flexible input |
| `make_sheets.py` | `CharacterRenderer` (Jinja2), entry point `main()`, PDF/ePub pipeline |
| `readers.py` | Parses Python character files, VTT JSON exports, parent sheet inheritance |
| `classes/` | `CharClass` subclasses (Wizard, Fighter, Cleric, etc.) — **not** subclasses of `Character` |
| `features/` | `Feature` subclasses; ~20 modules split by class/race/feat |
| `spells/` | 800+ spells split alphabetically across `spells_a.py`–`spells_z.py` |
| `forms/` | Jinja2 templates (`.tex`, `.html`, `.txt`) for output rendering |
| `data/` | YAML files for backgrounds, magic items, spell data |

## CI/CD Pipeline

The project uses GitHub Actions for continuous integration and deployment:

### Manual Workflow Triggers

Both workflows support manual triggering through GitHub's UI:

1. **Triggering Workflows**:

   - Go to Actions tab in the repository
   - Select the workflow (Python package or Docker)
   - Click "Run workflow" button
   - Choose:
     - Branch to run against
     - Input parameters (if any)

2. **Use Cases**:

   - Testing changes before committing
   - Rebuilding failed runs
   - Generating container images for testing
   - Validating specific Python versions

3. **Monitoring**:

   ```bash
   # Check status of PR checks
   gh pr checks 1

   # View workflow run logs
   gh run view <run-id>

   # Download artifacts from a run
   gh run download <run-id>
   ```

### Python CI Workflow

Tests run on all supported Python versions (3.10-3.13):

1. **Environment Setup**:

   - Installs system dependencies (pdftk, texlive)
   - Configures Python environment

   ```yaml
   sudo apt-get -y install pdftk texlive-latex-base texlive-latex-extra texlive-fonts-recommended
   ```

2. **Test Suite**:

   - Runs pytest with coverage reporting
   - Validates code style and formatting with Ruff
   - Tests example character generation

   ```bash
   pytest --cov=dungeonsheets tests/
   ruff check dungeonsheets/
   ruff format --check dungeonsheets/
   ```

3. **Output Format Validation**:
   ```bash
   makesheets --debug          # Standard PDF
   makesheets --debug --fancy  # Enhanced formatting
   makesheets --debug --output-format=epub  # ePub generation
   ```

### Docker Workflow

Builds and publishes container images:

1. **Multi-architecture Support**:

   - Builds for amd64 and arm64
   - Uses QEMU and Docker Buildx

2. **Container Registry**:

   - Publishes to GitHub Container Registry (GHCR)
   - Tags: `main` (latest development), version tags for releases

   ```bash
   docker pull ghcr.io/stiffneckjim/dungeon-sheets:main
   ```

3. **Container Features**:
   - Ubuntu-based with all dependencies pre-installed
   - Mounts current directory as `/build` for character files
   - Includes latest package version from branch/tag

## Key Workflows

### Dependency Management

This project uses **[uv](https://docs.astral.sh/uv/)** for fast, reliable Python package management:

```bash
uv sync              # Install all dependencies from uv.lock
uv sync --all-extras # Install with all optional dependencies (dev, etc.)
uv add package-name  # Add a new dependency
uv remove package-name # Remove a dependency
uv lock              # Update uv.lock after changing pyproject.toml
```

**Important**: Always use `uv` commands instead of `pip` for consistency. The `uv.lock` file ensures reproducible builds and is automatically used in CI/CD and devcontainers.

## Key Conventions

### Content Registration

New content (spells, features, armor, etc.) is registered by calling `default_content_registry.add_module(__name__)` at module level — **not** with a decorator:

```python
from dungeonsheets.content_registry import default_content_registry

default_content_registry.add_module(__name__)

class MySpell(Spell):
    name = "My Spell"
    level = 2
    ...
```

The registry resolves `"my spell"`, `"MySpell"`, or `"my_spell"` to the same class.

### Flexible Input Resolution

`Character.set_attrs()` and most setters accept strings, classes, or instances interchangeably. `_resolve_mechanic()` in `content.py` handles the coercion. This means:

```python
# All equivalent in a character file:
armor = "leather armor"
armor = LeatherArmor
armor = LeatherArmor()
```

### Adding New Content

1. Define your class in the appropriate module (e.g., `features/fighter.py`, `spells/spells_m.py`)
2. Ensure `default_content_registry.add_module(__name__)` is called in that module
3. Reference by name string in character files — no explicit import needed

For weapons/armor with bonuses, use the `improved_version()` classmethod pattern:
```python
# Creates "+2 Shortsword" dynamically
weapons = ["+2 shortsword"]
```

### Character Class vs D&D Class

- `Character` (in `character.py`): the player character object — **not** subclassed for D&D classes
- `CharClass` (in `classes/`): represents a D&D class (Fighter, Wizard, etc.) — assigned to a character via `add_class()`
- A `Character` holds a list of `CharClass` instances in `class_list`

### Parent Sheets

Character files can inherit from other character files:
```python
# wizard1.py
parent_sheets = ["base_character.py"]
name = "Gandalf"
# Other fields override the parent
```

### Homebrew Content

```python
from dungeonsheets import import_homebrew
campaign = import_homebrew("my_homebrew.py")
```

### YAML-Generated Content

Backgrounds and some magic items are generated dynamically from YAML files at import time via `yaml_content.py`. Don't expect to find these as explicit Python classes — they're constructed programmatically from `data/backgrounds.yaml` and similar.

## Project Conventions

1. **D&D Classes** (`classes/`): Subclass `CharClass`; define `name`, `hit_dice`, `spellcasting_ability`, `skill_proficiencies`, and feature lists.

2. **Features** (`features/`): Subclass `Feature`; define `name`, `description`, optionally `weapon_func(weapon)` to modify weapon stats. Accept `owner` in `__init__`.

3. **Testing**: Use `unittest.TestCase`. Mock external binaries (pdftk, pdflatex). Test string-to-class resolution explicitly.

4. **Exceptions**: Use `dungeonsheets.exceptions` — `ContentNotFound`, `AmbiguousContent`, etc. Don't raise raw `ValueError` for missing content.

## Integration Points

1. **PDF Generation**:
   - Primary: `pdftk` for form filling
   - Fallback: `pypdf` library
   - LaTeX (`pdflatex`) for additional pages (features, subclasses, magic items, spellbook, GM notes); `--fancy` toggles DnD-themed decorations for these LaTeX/HTML-rendered extra pages (spell sheets remain fillable PDF templates)

2. **Data Import**:
   - Python character files (primary)
   - VTT JSON exports (see `dungeonsheets/readers.py` for supported formats)

## Common Pitfalls

1. **Content not found**: Strings in character files should match a registered class name. Unknown strings are typically resolved via `_resolve_mechanic()` to a generic placeholder with a warning, which may lead to incorrect stats or sheet output even if loading appears to succeed. Check spelling and that the module containing the class calls `add_module()`.
2. **D&D class vs Character class**: Never subclass `Character` for a D&D class — use `CharClass`.
3. **PDF dependencies**: `pdftk` and `pdflatex` are external binaries; tests mock them. Don't assume they're available in all environments.
4. **Spells split by file**: When adding a spell, add it to the correct alphabetical file (`spells/spells_m.py` for "Magic Missile", etc.).

## Example Files

Check these files to understand common patterns:

- Basic character: `examples/wizard1.py`
- Complex character: `examples/multiclass1.py`
- GM notes: `examples/gm-campaign-notes.py`
- Test patterns: `tests/test_character.py`


## Command Formatting Preference

When providing terminal commands, present them individually in separate code blocks rather than grouped together. This makes it easier to copy and paste commands one at a time for execution.

Example of preferred format:
```bash
cd /some/directory
```

```bash
git status
```

Rather than:
```bash
cd /some/directory
git status
```

