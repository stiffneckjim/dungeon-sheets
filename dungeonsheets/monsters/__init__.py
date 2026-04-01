from pathlib import Path

from dungeonsheets.content_registry import default_content_registry
from dungeonsheets.monsters.monsters import *
from dungeonsheets.monsters.monsters import Monster
from dungeonsheets.yaml_content import load_yaml_monster_classes

_DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "monsters"

globals().update(
    load_yaml_monster_classes(
        _DATA_DIR,
        Monster,
        module=__name__,
    )
)

default_content_registry.add_module(__name__)
