from importlib.resources import files

from dungeonsheets.content_registry import default_content_registry
from dungeonsheets.spells.spells import Spell, create_spell
from dungeonsheets.spells.spells import all_spells as _all_spells
from dungeonsheets.yaml_content import load_yaml_spell_classes

_yaml_loaded = False


def _load_yaml_content():
    global _yaml_loaded
    if _yaml_loaded:
        return

    data_dir = files("dungeonsheets.data")
    spells_source = data_dir.joinpath("spells")
    if not spells_source.is_dir():
        spells_source = data_dir.joinpath("spells.yaml")

    globals().update(
        load_yaml_spell_classes(
            spells_source,
            Spell,
            module=__name__,
        )
    )
    _yaml_loaded = True


def all_spells():
    _load_yaml_content()
    return _all_spells()


def __getattr__(name):
    _load_yaml_content()
    try:
        return globals()[name]
    except KeyError as exc:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}") from exc


def __dir__():
    _load_yaml_content()
    return sorted(globals())


default_content_registry.add_module(__name__)
