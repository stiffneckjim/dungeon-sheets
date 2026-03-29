"""Helpers for loading canonical content definitions from YAML files."""

from pathlib import Path

import yaml


def _resolve_yaml_sources(yaml_path):
    """Resolve YAML source files from either a file path or directory path.

    Parameters
    ----------
    yaml_path : PathLike
        A YAML file path or a directory containing YAML files.

    Returns
    -------
    list[Path]
        Sorted list of YAML files to load.
    """
    path = Path(yaml_path)
    if path.is_dir():
        return sorted(candidate for candidate in path.glob("*.yaml") if candidate.is_file())
    if path.exists() and path.is_file():
        return [path]
    return []


def _load_yaml_list_entries(yaml_file, content_label):
    """Load and validate list-based YAML entries from a file."""
    raw_data = yaml.safe_load(yaml_file.read_text(encoding="utf-8")) or []
    if not isinstance(raw_data, list):
        raise ValueError(f"Expected a list of {content_label} definitions in {yaml_file}")
    return raw_data


def load_yaml_background_classes(yaml_path, base_class, features_module):
    """Build background classes from a YAML file.

    Parameters
    ----------
    yaml_path : PathLike
        Location of the YAML file containing background definitions.
    base_class : type
        The base background class to inherit from.
    features_module : module
        Module containing feature classes referenced by name.

    Returns
    -------
    dict[str, type]
        Mapping of generated class names to generated background classes.
    """
    generated_classes = {}
    class_sources = {}
    for yaml_file in _resolve_yaml_sources(yaml_path):
        for entry in _load_yaml_list_entries(yaml_file, "background"):
            class_name = entry["class_name"]
            if class_name in class_sources:
                raise ValueError(
                    f"Duplicate background class_name '{class_name}' found in "
                    f"{class_sources[class_name]} and {yaml_file}"
                )
            class_sources[class_name] = yaml_file

            attrs = {
                "__doc__": entry.get(
                    "description", f"{entry.get('name', class_name)} background loaded from YAML."
                ),
                "name": entry.get("name", class_name),
                "skill_proficiencies": tuple(entry.get("skill_proficiencies", [])),
                "weapon_proficiencies": tuple(entry.get("weapon_proficiencies", [])),
                "proficiencies_text": tuple(entry.get("proficiencies_text", [])),
                "skill_choices": tuple(entry.get("skill_choices", [])),
                "num_skill_choices": entry.get("num_skill_choices", 0),
                "languages": tuple(entry.get("languages", [])),
                "features": tuple(
                    getattr(features_module, feature_name)
                    for feature_name in entry.get("features", [])
                ),
                "data_source": "yaml",
            }
            generated_classes[class_name] = type(class_name, (base_class,), attrs)

    return generated_classes


def load_yaml_spell_classes(yaml_path, base_class):
    """Build spell classes from a YAML file.

    Parameters
    ----------
    yaml_path : PathLike
        Location of the YAML file containing spell definitions.
    base_class : type
        The base spell class to inherit from.

    Returns
    -------
    dict[str, type]
        Mapping of generated class names to generated spell classes.
    """
    generated_classes = {}
    class_sources = {}
    for yaml_file in _resolve_yaml_sources(yaml_path):
        for entry in _load_yaml_list_entries(yaml_file, "spell"):
            class_name = entry["class_name"]
            if class_name in class_sources:
                raise ValueError(
                    f"Duplicate spell class_name '{class_name}' found in "
                    f"{class_sources[class_name]} and {yaml_file}"
                )
            class_sources[class_name] = yaml_file

            attrs = {
                "__doc__": entry.get(
                    "description", f"{entry.get('name', class_name)} spell loaded from YAML."
                ),
                "name": entry.get("name", class_name),
                "level": entry.get("level", 0),
                "casting_time": entry.get("casting_time", "1 action"),
                "casting_range": entry.get("casting_range", "60 feet"),
                "components": tuple(entry.get("components", [])),
                "materials": entry.get("materials", ""),
                "duration": entry.get("duration", "Instantaneous"),
                "ritual": entry.get("ritual", False),
                "magic_school": entry.get("magic_school", ""),
                "classes": tuple(entry.get("classes", [])),
                "data_source": "yaml",
            }
            generated_classes[class_name] = type(class_name, (base_class,), attrs)

    return generated_classes


def load_yaml_magic_item_classes(yaml_path, base_class):
    """Build magic item classes from a YAML file.

    Parameters
    ----------
    yaml_path : PathLike
        Location of the YAML file containing magic item definitions.
    base_class : type
        The base magic item class to inherit from.

    Returns
    -------
    dict[str, type]
        Mapping of generated class names to generated magic item classes.
    """
    generated_classes = {}
    class_sources = {}
    for yaml_file in _resolve_yaml_sources(yaml_path):
        for entry in _load_yaml_list_entries(yaml_file, "magic item"):
            class_name = entry["class_name"]
            if class_name in class_sources:
                raise ValueError(
                    f"Duplicate magic item class_name '{class_name}' found in "
                    f"{class_sources[class_name]} and {yaml_file}"
                )
            class_sources[class_name] = yaml_file

            attrs = {
                "__doc__": entry.get(
                    "description", f"{entry.get('name', class_name)} magic item loaded from YAML."
                ),
                "name": entry.get("name", class_name),
                "rarity": entry.get("rarity", ""),
                "item_type": entry.get("item_type", ""),
                "requires_attunement": entry.get("requires_attunement", False),
                "ac_bonus": entry.get("ac_bonus", 0),
                "st_bonus_all": entry.get("st_bonus_all", 0),
                "st_bonus_strength": entry.get("st_bonus_strength"),
                "st_bonus_dexterity": entry.get("st_bonus_dexterity"),
                "st_bonus_constitution": entry.get("st_bonus_constitution"),
                "st_bonus_intelligence": entry.get("st_bonus_intelligence"),
                "st_bonus_wisdom": entry.get("st_bonus_wisdom"),
                "st_bonus_charisma": entry.get("st_bonus_charisma"),
                "weapon_attack_bonus": entry.get("weapon_attack_bonus", 0),
                "weapon_damage_bonus": entry.get("weapon_damage_bonus", 0),
                "passive_effect_description": entry.get("passive_effect_description", ""),
                "passive_effect_value": entry.get("passive_effect_value", 0),
                "linked_spells": tuple(entry.get("linked_spells", [])),
                "charge_pool_max": entry.get("charge_pool_max", 0),
                "charge_recharge_rule": entry.get("charge_recharge_rule", ""),
                "data_source": "yaml",
            }
            generated_classes[class_name] = type(class_name, (base_class,), attrs)

    return generated_classes
