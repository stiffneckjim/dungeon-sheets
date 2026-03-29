from pathlib import Path

from dungeonsheets.content_registry import default_content_registry
from dungeonsheets.spells.spells import Spell, all_spells, create_spell
from dungeonsheets.yaml_content import load_yaml_spell_classes

_DATA_DIR = Path(__file__).resolve().parent.parent.joinpath("data")
_SPELLS_YAML_SOURCE = (
    _DATA_DIR.joinpath("spells")
    if _DATA_DIR.joinpath("spells").is_dir()
    else _DATA_DIR.joinpath("spells.yaml")
)

globals().update(
    load_yaml_spell_classes(
        _SPELLS_YAML_SOURCE,
        Spell,
        module=__name__,
    )
)

default_content_registry.add_module(__name__)
