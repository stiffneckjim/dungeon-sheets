"""Helpers for loading canonical content definitions from YAML files."""

import re
from pathlib import Path

import yaml


def _validate_list_field(entry, field, yaml_file):
    """Raise ValueError if *field* exists in *entry* but is not a list.

    Catches the common YAML authoring mistake of writing a bare string instead
    of a single-element list, which would otherwise silently iterate over the
    string's characters when converted to a tuple.
    """
    value = entry.get(field)
    if value is not None and not isinstance(value, list):
        raise ValueError(
            f"Field '{field}' in '{entry.get('class_name', '?')}' must be a list "
            f"(got {type(value).__name__!r}) in {yaml_file}"
        )


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


def _parse_monster_speeds(speed_str):
    """Parse a speed string into component speed fields.

    Parameters
    ----------
    speed_str : str
        Speed string from YAML, e.g. ``"30 ft."`` or ``"40 ft., fly 80 ft., swim 30 ft."``.

    Returns
    -------
    dict
        Keys: ``speed``, ``fly_speed``, ``swim_speed``, ``climb_speed``, ``burrow_speed``
        (all integers).
    """
    result = {"speed": 0, "fly_speed": 0, "swim_speed": 0, "climb_speed": 0, "burrow_speed": 0}
    if not speed_str:
        return result
    named = re.compile(r"(fly|swim|climb|burrow)\s+(\d+)", re.IGNORECASE)
    for match in named.finditer(speed_str):
        kind, value = match.group(1).lower(), int(match.group(2))
        result[f"{kind}_speed"] = value
    base = re.match(r"(\d+)", speed_str)
    if base:
        result["speed"] = int(base.group(1))
    return result


def _build_monster_docstring(description, traits, actions, legendary_actions, reactions):
    """Build a structured monster docstring matching the format used by Python monster classes.

    The format mirrors the existing docstrings in the ``monsters_*.py`` files:
    description text, then traits, then a ``# Actions`` section divider, then
    actions, and optionally ``# Legendary Actions`` and ``# Reactions`` sections.

    Parameters
    ----------
    description : str
    traits : list[dict]
    actions : list[dict]
    legendary_actions : list[dict]
    reactions : list[dict]

    Returns
    -------
    str
    """
    # Strip any legacy "# Actions" block from the free-text description;
    # actions are represented by the structured list and appended below.
    raw_desc = (description or "").split("# Actions")[0]
    # Normalize each line to 0 indentation so RST does not interpret
    # wrapped continuation lines as definition-list entries, which would
    # emit \item commands that break LaTeX rendering.
    clean_description = "\n".join(line.strip() for line in raw_desc.splitlines()).strip()
    parts = [clean_description]
    for trait in traits:
        parts.append(f"\n{trait['name']}.\n  {trait['description']}")
    # Use 4-space indent before "#" so RPGtex_monster_info (latex.py) correctly
    # splits feats from actions when rendering the DnD monster block.
    parts.append("\n    # Actions")
    for action in actions:
        parts.append(f"\n{action['name']}.\n  {action['description']}")
    if legendary_actions:
        parts.append("\n    # Legendary Actions")
        for la in legendary_actions:
            parts.append(f"\n{la['name']}.\n  {la['description']}")
    if reactions:
        parts.append("\n    # Reactions")
        for reaction in reactions:
            parts.append(f"\n{reaction['name']}.\n  {reaction['description']}")
    return "\n".join(parts)


def load_yaml_background_classes(yaml_path, base_class, features_module, module=None):
    """Build background classes from a YAML file.

    Parameters
    ----------
    yaml_path : PathLike
        Location of the YAML file containing background definitions.
    base_class : type
        The base background class to inherit from.
    features_module : module
        Module containing feature classes referenced by name.
    module : str, optional
        Value to assign to ``__module__`` on each generated class. Pass
        ``__name__`` from the calling module so that introspection and repr
        reflect where the class is actually injected, not this helper module.

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

            for list_field in (
                "skill_proficiencies",
                "weapon_proficiencies",
                "proficiencies_text",
                "skill_choices",
                "languages",
                "features",
            ):
                _validate_list_field(entry, list_field, yaml_file)

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
            if module is not None:
                attrs["__module__"] = module
            generated_classes[class_name] = type(class_name, (base_class,), attrs)

    return generated_classes


def load_yaml_spell_classes(yaml_path, base_class, module=None):
    """Build spell classes from a YAML file.

    Parameters
    ----------
    yaml_path : PathLike
        Location of the YAML file containing spell definitions.
    base_class : type
        The base spell class to inherit from.
    module : str, optional
        Value to assign to ``__module__`` on each generated class. Pass
        ``__name__`` from the calling module so that introspection and repr
        reflect where the class is actually injected, not this helper module.

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

            for list_field in ("classes", "components"):
                _validate_list_field(entry, list_field, yaml_file)

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
            if module is not None:
                attrs["__module__"] = module
            generated_classes[class_name] = type(class_name, (base_class,), attrs)

    return generated_classes


def load_yaml_monster_classes(yaml_path, base_class, module=None):
    """Build monster classes from a YAML file.

    Parameters
    ----------
    yaml_path : PathLike
        Location of the YAML file (or directory of YAML files) containing monster definitions.
    base_class : type
        The base monster class to inherit from.
    module : str, optional
        Value to assign to ``__module__`` on each generated class. Pass
        ``__name__`` from the calling module so that introspection and repr
        reflect where the class is actually injected, not this helper module.

    Returns
    -------
    dict[str, type]
        Mapping of generated class names to generated monster classes.
    """
    from dungeonsheets.stats import Ability

    generated_classes = {}
    class_sources = {}
    for yaml_file in _resolve_yaml_sources(yaml_path):
        for entry in _load_yaml_list_entries(yaml_file, "monster"):
            class_name = entry["class_name"]
            if class_name in class_sources:
                raise ValueError(
                    f"Duplicate monster class_name '{class_name}' found in "
                    f"{class_sources[class_name]} and {yaml_file}"
                )
            class_sources[class_name] = yaml_file

            for list_field in ("traits", "actions", "legendary_actions", "reactions"):
                _validate_list_field(entry, list_field, yaml_file)

            description_text = entry.get(
                "description", f"{entry.get('name', class_name)} monster loaded from YAML."
            )
            traits_list = [
                {"name": t.get("name", ""), "description": t.get("description", "")}
                for t in entry.get("traits", [])
            ]
            actions_list = [
                {"name": a.get("name", ""), "description": a.get("description", "")}
                for a in entry.get("actions", [])
            ]
            legendary_actions_list = [
                {"name": la.get("name", ""), "description": la.get("description", "")}
                for la in entry.get("legendary_actions", [])
            ]
            reactions_list = [
                {"name": r.get("name", ""), "description": r.get("description", "")}
                for r in entry.get("reactions", [])
            ]
            speeds = _parse_monster_speeds(entry.get("speed", ""))

            attrs = {
                "__doc__": _build_monster_docstring(
                    description_text,
                    traits_list,
                    actions_list,
                    legendary_actions_list,
                    reactions_list,
                ),
                "name": entry.get("name", class_name),
                "description": entry.get("creature_type") or description_text,
                "challenge_rating": entry.get("challenge_rating", 0),
                "armor_class": entry.get("armor_class", 10),
                "hp_max": entry.get("hp_max", 1),
                "speed": speeds["speed"],
                "fly_speed": speeds["fly_speed"],
                "swim_speed": speeds["swim_speed"],
                "climb_speed": speeds["climb_speed"],
                "burrow_speed": speeds["burrow_speed"],
                "strength": Ability(int(entry.get("strength", 10))),
                "dexterity": Ability(int(entry.get("dexterity", 10))),
                "constitution": Ability(int(entry.get("constitution", 10))),
                "intelligence": Ability(int(entry.get("intelligence", 10))),
                "wisdom": Ability(int(entry.get("wisdom", 10))),
                "charisma": Ability(int(entry.get("charisma", 10))),
                "skills": entry.get("skills", entry.get("skill_str", "")),
                "saving_throws": entry.get("saving_throws", ""),
                "damage_immunities": entry.get("damage_immunities", ""),
                "damage_resistances": entry.get("damage_resistances", ""),
                "damage_vulnerabilities": entry.get("damage_vulnerabilities", ""),
                "condition_immunities": entry.get("condition_immunities", ""),
                "senses": entry.get("senses", ""),
                "languages": entry.get("languages", ""),
                "traits": traits_list,
                "actions": actions_list,
                "legendary_actions": legendary_actions_list,
                "reactions": reactions_list,
                "data_source": "yaml",
            }
            if module is not None:
                attrs["__module__"] = module
            else:
                attrs["__module__"] = __name__
            generated_classes[class_name] = type(class_name, (base_class,), attrs)

    return generated_classes


def load_yaml_magic_item_classes(yaml_path, base_class, module=None):
    """Build magic item classes from a YAML file.

    Parameters
    ----------
    yaml_path : PathLike
        Location of the YAML file containing magic item definitions.
    base_class : type
        The base magic item class to inherit from.
    module : str, optional
        Value to assign to ``__module__`` on each generated class. Pass
        ``__name__`` from the calling module so that introspection and repr
        reflect where the class is actually injected, not this helper module.

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

            _validate_list_field(entry, "linked_spells", yaml_file)

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
            if module is not None:
                attrs["__module__"] = module
            generated_classes[class_name] = type(class_name, (base_class,), attrs)

    return generated_classes


def load_yaml_weapon_classes(yaml_path, base_class, type_map=None, module=None):
    """Build weapon classes from a YAML file.

    Parameters
    ----------
    yaml_path : PathLike
        Location of the YAML file containing weapon definitions.
    base_class : type
        Fallback base class when a weapon's ``weapon_type`` is absent or not
        in *type_map*.
    type_map : dict[str, tuple[type, ...]], optional
        Mapping from ``weapon_type`` strings (e.g. ``"simple melee"``,
        ``"firearm"``) to a tuple of base classes to inherit from.  When
        provided, entries whose ``weapon_type`` matches will use the
        corresponding tuple instead of *(base_class,)*.
    module : str, optional
        Value to assign to ``__module__`` on each generated class. Pass
        ``__name__`` from the calling module so that introspection and repr
        reflect where the class is actually injected, not this helper module.

    Returns
    -------
    dict[str, type]
        Mapping of generated class names to generated weapon classes.
    """
    generated_classes = {}
    class_sources = {}
    for yaml_file in _resolve_yaml_sources(yaml_path):
        for entry in _load_yaml_list_entries(yaml_file, "weapon"):
            class_name = entry["class_name"]
            if class_name in class_sources:
                raise ValueError(
                    f"Duplicate weapon class_name '{class_name}' found in "
                    f"{class_sources[class_name]} and {yaml_file}"
                )
            class_sources[class_name] = yaml_file

            weapon_type = entry.get("weapon_type", "")
            if type_map is not None and weapon_type in type_map:
                bases = type_map[weapon_type]
            else:
                bases = (base_class,)

            attrs = {
                "name": entry.get("name", class_name),
                "base_damage": str(entry.get("base_damage", "1d4")),
                "damage_type": entry.get("damage_type", ""),
                "weight": entry.get("weight", 0),
                "cost": str(entry.get("cost", "0 gp")),
                "properties": entry.get("properties", ""),
                "ability": entry.get("ability", "strength"),
                "is_finesse": entry.get("is_finesse", False),
                "damage_bonus": entry.get("damage_bonus", 0),
                "attack_bonus": entry.get("attack_bonus", 0),
                "data_source": "yaml",
            }
            if module is not None:
                attrs["__module__"] = module
            else:
                attrs["__module__"] = __name__
            generated_classes[class_name] = type(class_name, bases, attrs)

    return generated_classes


def load_yaml_armor_classes(yaml_path, base_class, module=None, type_map=None):
    """Build armor classes from a YAML file.

    Parameters
    ----------
    yaml_path : PathLike
        Location of the YAML file containing armor definitions.
    base_class : type
        The default base armor class to inherit from when *armor_type* is not
        present in *type_map* or is absent.
    module : str, optional
        Value to assign to ``__module__`` on each generated class. Pass
        ``__name__`` from the calling module so that introspection and repr
        reflect where the class is actually injected, not this helper module.
    type_map : dict[str, type], optional
        Mapping from ``armor_type`` string values (e.g. ``"light"``,
        ``"medium"``, ``"heavy"``) to the concrete base class to inherit from.
        When provided, YAML entries whose ``armor_type`` key matches will
        inherit from the corresponding class instead of *base_class*.

    Returns
    -------
    dict[str, type]
        Mapping of generated class names to generated armor classes.
    """
    generated_classes = {}
    class_sources = {}
    for yaml_file in _resolve_yaml_sources(yaml_path):
        for entry in _load_yaml_list_entries(yaml_file, "armor"):
            class_name = entry["class_name"]
            if class_name in class_sources:
                raise ValueError(
                    f"Duplicate armor class_name '{class_name}' found in "
                    f"{class_sources[class_name]} and {yaml_file}"
                )
            class_sources[class_name] = yaml_file

            armor_type = entry.get("armor_type", "")
            parent = base_class
            if type_map is not None:
                parent = type_map.get(armor_type, base_class)

            attrs = {
                "__doc__": entry.get(
                    "description",
                    f"{entry.get('name', class_name)} armor loaded from YAML.",
                ),
                "name": entry.get("name", class_name),
                "base_armor_class": entry.get(
                    "base_armor_class", getattr(parent, "base_armor_class", 10)
                ),
                "dexterity_mod_max": entry.get(
                    "dexterity_mod_max", getattr(parent, "dexterity_mod_max", None)
                ),
                "strength_required": entry.get("strength_required"),
                "stealth_disadvantage": entry.get("stealth_disadvantage", False),
                "weight": entry.get("weight", 0),
                "cost": entry.get("cost", "0 gp"),
                "armor_type": armor_type,
                "data_source": "yaml",
            }
            if module is not None:
                attrs["__module__"] = module
            generated_classes[class_name] = type(class_name, (parent,), attrs)

    return generated_classes
