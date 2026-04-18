from importlib.resources import files

from dungeonsheets.content_registry import default_content_registry
from dungeonsheets.monsters.monsters import *
from dungeonsheets.monsters.monsters import Monster
from dungeonsheets.yaml_content import load_yaml_monster_classes

_yaml_loaded = False


_LEGACY_MONSTER_CLASSES = {
    name: obj
    for name, obj in list(globals().items())
    if isinstance(obj, type) and issubclass(obj, Monster) and obj is not Monster
}

# Remove concrete monster class bindings so first access triggers __getattr__
# and loads YAML-backed classes before exposing legacy fallbacks.
for _name in _LEGACY_MONSTER_CLASSES:
    globals().pop(_name, None)


def _load_yaml_content():
    global _yaml_loaded
    if _yaml_loaded:
        return

    generated = load_yaml_monster_classes(
        files("dungeonsheets.data").joinpath("monsters"),
        Monster,
        module=__name__,
    )
    globals().update(_LEGACY_MONSTER_CLASSES)
    globals().update(generated)

    _yaml_loaded = True


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
