from pathlib import Path

from dungeonsheets.content_registry import default_content_registry
from dungeonsheets.spells.spells import Spell, all_spells, create_spell
from dungeonsheets.spells.spells_a import *
from dungeonsheets.spells.spells_b import *
from dungeonsheets.spells.spells_c import *
from dungeonsheets.spells.spells_d import *
from dungeonsheets.spells.spells_e import *
from dungeonsheets.spells.spells_f import *
from dungeonsheets.spells.spells_g import *
from dungeonsheets.spells.spells_h import *
from dungeonsheets.spells.spells_i import *
from dungeonsheets.spells.spells_j import *
from dungeonsheets.spells.spells_k import *
from dungeonsheets.spells.spells_l import *
from dungeonsheets.spells.spells_m import *
from dungeonsheets.spells.spells_n import *
from dungeonsheets.spells.spells_o import *
from dungeonsheets.spells.spells_p import *
from dungeonsheets.spells.spells_q import *
from dungeonsheets.spells.spells_r import *
from dungeonsheets.spells.spells_s import *
from dungeonsheets.spells.spells_t import *
from dungeonsheets.spells.spells_u import *
from dungeonsheets.spells.spells_v import *
from dungeonsheets.spells.spells_w import *
from dungeonsheets.spells.spells_x import *
from dungeonsheets.spells.spells_y import *
from dungeonsheets.spells.spells_z import *
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
