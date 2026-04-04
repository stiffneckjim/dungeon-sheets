#!/usr/bin/env python
"""Convert Monster Python class files to per-letter YAML data files.

Usage:
    uv run python scripts/convert_monsters.py
"""

from __future__ import annotations

import importlib
import inspect
import re
import sys
import textwrap
from pathlib import Path


# ---------------------------------------------------------------------------
# Docstring parser
# ---------------------------------------------------------------------------

SECTION_HEADERS = re.compile(
    r"^#\s*(Actions|Legendary Actions|Reactions|Lair Actions|Bonus Actions)\s*$",
    re.MULTILINE,
)


def _split_sections(doc: str) -> dict[str, str]:
    """Split a monster docstring into named sections.

    Returns a dict with keys: "traits", "actions", "legendary_actions",
    "reactions" — each mapped to the raw text for that section.
    """
    sections: dict[str, str] = {
        "traits": "",
        "actions": "",
        "legendary_actions": "",
        "reactions": "",
    }

    # Find all section header positions
    matches = list(SECTION_HEADERS.finditer(doc))
    if not matches:
        # Entire doc is traits
        sections["traits"] = doc
        return sections

    # Text before first header = traits
    sections["traits"] = doc[: matches[0].start()]

    for i, m in enumerate(matches):
        header = m.group(1).lower().replace(" ", "_")
        end = matches[i + 1].start() if i + 1 < len(matches) else len(doc)
        content = doc[m.end() : end]
        if header in sections:
            sections[header] += content
        # lair_actions and bonus_actions are intentionally ignored

    return sections


def _parse_entries(text: str) -> list[dict[str, str]]:
    """Parse a block of trait/action text into a list of {name, description} dicts.

    The expected format is:
        Name.
          Description line one.
          Description line two.
        NextName.
          ...

    A line that starts without leading whitespace and contains non-whitespace
    characters is treated as a name line (possibly ending with a period).
    Subsequent indented lines are the description.
    """
    entries: list[dict[str, str]] = []
    current_name: str | None = None
    desc_lines: list[str] = []

    def _flush():
        if current_name is not None:
            desc = " ".join(line.strip() for line in desc_lines if line.strip())
            entries.append({"name": current_name, "description": desc})

    for raw_line in text.splitlines():
        # Skip blank lines between entries
        if not raw_line.strip():
            continue

        # A name line: starts with a non-whitespace character
        if raw_line and not raw_line[0].isspace():
            _flush()
            current_name = raw_line.strip().rstrip(".")
            desc_lines = []
        else:
            desc_lines.append(raw_line)

    _flush()
    return entries


def _extract_monster_data(cls) -> dict:
    """Extract all relevant attributes from a Monster subclass."""
    doc = (cls.__doc__ or "").strip()
    sections = _split_sections(doc)

    traits = _parse_entries(sections["traits"])
    actions = _parse_entries(sections["actions"])
    legendary_actions = _parse_entries(sections["legendary_actions"])
    reactions = _parse_entries(sections["reactions"])

    speed_val = getattr(cls, "speed", 30)
    if isinstance(speed_val, int):
        speed_str = f"{speed_val} ft."
    else:
        speed_str = str(speed_val)

    def _ability_int(attr: str) -> int:
        val = cls.__dict__.get(attr) or getattr(cls, attr, None)
        if val is None:
            return 10
        # Ability is a descriptor — read .default_value directly from the class dict
        from dungeonsheets.stats import Ability as _Ability

        if isinstance(val, _Ability):
            return val.default_value
        try:
            return int(val)
        except (TypeError, ValueError):
            return 10

    data: dict = {
        "class_name": cls.__name__,
        "name": getattr(cls, "name", cls.__name__),
        "creature_type": getattr(cls, "description", ""),
        "challenge_rating": getattr(cls, "challenge_rating", 0),
        "armor_class": getattr(cls, "armor_class", 10),
        "hp_max": getattr(cls, "hp_max", 1),
        "speed": speed_str,
        "strength": _ability_int("strength"),
        "dexterity": _ability_int("dexterity"),
        "constitution": _ability_int("constitution"),
        "intelligence": _ability_int("intelligence"),
        "wisdom": _ability_int("wisdom"),
        "charisma": _ability_int("charisma"),
        "skill_str": getattr(cls, "skills", ""),
        "saving_throws": getattr(cls, "saving_throws", ""),
        "senses": getattr(cls, "senses", ""),
        "languages": getattr(cls, "languages", ""),
        "damage_immunities": getattr(cls, "damage_immunities", ""),
        "damage_resistances": getattr(cls, "damage_resistances", ""),
        "damage_vulnerabilities": getattr(cls, "damage_vulnerabilities", ""),
        "condition_immunities": getattr(cls, "condition_immunities", ""),
        "description": doc,
        "traits": traits,
        "actions": actions,
        "legendary_actions": legendary_actions,
        "reactions": reactions,
    }
    return data


# ---------------------------------------------------------------------------
# YAML serialiser (hand-rolled for clean output)
# ---------------------------------------------------------------------------


def _yaml_str(value: str) -> str:
    """Return a YAML scalar for *value*, choosing the best style."""
    if not value:
        return '""'
    # Use block literal for multi-line strings
    if "\n" in value:
        indented = textwrap.indent(value.rstrip(), "    ")
        return f"|\n{indented}\n"
    # Quote strings that could be misinterpreted
    needs_quote = any(
        value.startswith(c) for c in (":", "-", "?", "#", "&", "*", "!", "|", ">", "'", '"', "{", "[")
    ) or ":" in value or "#" in value
    if needs_quote:
        escaped = value.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'
    return value


def _yaml_number(value) -> str:
    """Return a YAML scalar for a numeric challenge rating or integer."""
    if isinstance(value, float):
        # Represent fractions cleanly
        if value == 0.125:
            return "0.125"
        if value == 0.25:
            return "0.25"
        if value == 0.5:
            return "0.5"
        # General float — avoid scientific notation
        return f"{value:g}"
    return str(value)


def _yaml_entry_list(entries: list[dict], indent: int = 2) -> str:
    """Serialise a list of {name, description} dicts as YAML."""
    if not entries:
        return "[]\n"
    pad = " " * indent
    lines = ["\n"]
    for e in entries:
        name_val = _yaml_str(e.get("name", ""))
        desc_val = e.get("description", "")
        lines.append(f"{pad}- name: {name_val}\n")
        if "\n" in desc_val:
            indented = textwrap.indent(desc_val.rstrip(), f"{pad}    ")
            lines.append(f"{pad}  description: |\n{indented}\n")
        else:
            lines.append(f"{pad}  description: {_yaml_str(desc_val)}\n")
    return "".join(lines)


def _serialize_monster(data: dict) -> str:
    """Serialise a single monster data dict to YAML (as a list item)."""
    lines: list[str] = []
    lines.append(f"- class_name: {data['class_name']}\n")
    lines.append(f"  name: {_yaml_str(data['name'])}\n")

    if data.get("creature_type"):
        lines.append(f"  creature_type: {_yaml_str(data['creature_type'])}\n")

    lines.append(f"  challenge_rating: {_yaml_number(data['challenge_rating'])}\n")
    lines.append(f"  armor_class: {data['armor_class']}\n")
    lines.append(f"  hp_max: {data['hp_max']}\n")
    lines.append(f"  speed: {_yaml_str(data['speed'])}\n")

    for stat in ("strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"):
        lines.append(f"  {stat}: {data[stat]}\n")

    if data.get("skill_str"):
        lines.append(f"  skill_str: {_yaml_str(data['skill_str'])}\n")
    if data.get("saving_throws"):
        lines.append(f"  saving_throws: {_yaml_str(data['saving_throws'])}\n")
    if data.get("senses"):
        lines.append(f"  senses: {_yaml_str(data['senses'])}\n")
    if data.get("languages"):
        lines.append(f"  languages: {_yaml_str(data['languages'])}\n")
    if data.get("damage_immunities"):
        lines.append(f"  damage_immunities: {_yaml_str(data['damage_immunities'])}\n")
    if data.get("damage_resistances"):
        lines.append(f"  damage_resistances: {_yaml_str(data['damage_resistances'])}\n")
    if data.get("damage_vulnerabilities"):
        lines.append(f"  damage_vulnerabilities: {_yaml_str(data['damage_vulnerabilities'])}\n")
    if data.get("condition_immunities"):
        lines.append(f"  condition_immunities: {_yaml_str(data['condition_immunities'])}\n")

    desc = data.get("description", "")
    if desc:
        indented = textwrap.indent(desc.rstrip(), "    ")
        lines.append(f"  description: |\n{indented}\n")

    lines.append(f"  traits: {_yaml_entry_list(data['traits'])}")
    lines.append(f"  actions: {_yaml_entry_list(data['actions'])}")

    if data.get("legendary_actions"):
        lines.append(f"  legendary_actions: {_yaml_entry_list(data['legendary_actions'])}")
    if data.get("reactions"):
        lines.append(f"  reactions: {_yaml_entry_list(data['reactions'])}")

    return "".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(repo_root))

    from dungeonsheets.monsters.monsters import Monster

    out_dir = repo_root / "dungeonsheets" / "data" / "monsters"
    out_dir.mkdir(parents=True, exist_ok=True)

    total = 0
    for letter in "abcdefghijklmnopqrstuvwxyz":
        module_name = f"dungeonsheets.monsters.monsters_{letter}"
        try:
            mod = importlib.import_module(module_name)
        except ImportError as exc:
            print(f"  skip {module_name}: {exc}", file=sys.stderr)
            continue

        monsters = [
            cls
            for _, cls in inspect.getmembers(mod, inspect.isclass)
            if issubclass(cls, Monster) and cls is not Monster and cls.__module__ == module_name
        ]

        if not monsters:
            continue

        yaml_parts: list[str] = []
        for cls in monsters:
            entry_yaml = _serialize_monster(_extract_monster_data(cls))
            yaml_parts.append(entry_yaml)

        out_path = out_dir / f"monsters_{letter}.yaml"
        content = "\n".join(yaml_parts) + "\n"
        # Enforce LF line endings
        content = content.replace("\r\n", "\n")
        out_path.write_bytes(content.encode("utf-8"))
        total += len(monsters)
        print(f"  {out_path.name}: {len(monsters)} monsters")

    print(f"\nTotal: {total} monsters written to {out_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
