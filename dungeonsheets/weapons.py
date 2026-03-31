from pathlib import Path

from dungeonsheets.content_registry import default_content_registry
from dungeonsheets.yaml_content import load_yaml_weapon_classes

default_content_registry.add_module(__name__)

_DATA_DIR = Path(__file__).parent / "data"


class Weapon:
    """A weapon that be used to deal damage.

    Attributes
    ==========

    Parameters
    ==========
    wielder
      The character (or NPC) that is using the weapon.

    """

    name = ""
    cost = "0 gp"
    base_damage = "1d4"
    damage_bonus = 0
    attack_bonus = 0
    damage_type = "p"
    weight = 1  # In lbs
    properties = ""
    ability = "strength"
    is_finesse = False
    features_applied = False

    def __init__(self, wielder=None):
        self.wielder = wielder

    @classmethod
    def improved_version(cls, bonus):
        bonus = int(bonus)

        class NewWeapon(cls):
            name = f"+{bonus} " + cls.name
            damage_bonus = bonus
            attack_bonus = bonus

        return NewWeapon

    def apply_features(self):
        if (not self.features_applied) and (self.wielder is not None):
            self.features_applied = True
            for f in self.wielder.features:
                f.weapon_func(self)

    @property
    def ability_mod(self):
        if self.wielder is None:
            return 0
        else:
            if self.is_finesse:
                return max(self.wielder.strength.modifier, self.wielder.dexterity.modifier)
            else:
                return getattr(self.wielder, self.ability).modifier

    @property
    def attack_modifier(self):
        self.apply_features()
        mod = self.attack_bonus
        if self.wielder is not None:
            mod += self.ability_mod
            if self.wielder.is_proficient(self):
                mod += self.wielder.proficiency_bonus
        return mod

    @property
    def damage(self):
        self.apply_features()
        dam_str = str(self.base_damage)
        bonus = self.damage_bonus
        if self.wielder is not None:
            bonus += self.ability_mod
        if bonus != 0:
            dam_str += "{:+d}".format(bonus)
        return dam_str

    def __str__(self):
        return self.name

    def __repr__(self):
        return '"{:s}"'.format(self.name)


class MeleeWeapon(Weapon):
    name = "Melee Weapons"
    ability = "strength"


class RangedWeapon(Weapon):
    name = "Ranged Weapons"
    ability = "dexterity"


class SimpleWeapon(Weapon):
    name = "Simple Weapons"


class MartialWeapon(Weapon):
    name = "Martial Weapons"


class Unarmed(MeleeWeapon):
    name = "Unarmed"
    cost = "0 gp"
    base_damage = "1"
    damage_type = "b"
    weight = 0
    properties = ""
    ability = "strength"


class Firearm(RangedWeapon):
    name = "Firearm"
    ability = "dexterity"
    damage_type = "p"


MonkUnarmedStrike = Unarmed
UnarmedStrike = Unarmed

_TYPE_MAP = {
    "simple melee": (SimpleWeapon, MeleeWeapon),
    "simple ranged": (SimpleWeapon, RangedWeapon),
    "martial melee": (MartialWeapon, MeleeWeapon),
    "martial ranged": (MartialWeapon, RangedWeapon),
    "melee": (MeleeWeapon,),
    "ranged": (RangedWeapon,),
    "firearm": (Firearm,),
    "unarmed": (Unarmed,),
}

_generated = load_yaml_weapon_classes(
    _DATA_DIR / "weapons.yaml",
    Weapon,
    type_map=_TYPE_MAP,
    module=__name__,
)
globals().update(_generated)

# Category tuples rebuilt from loaded classes so existing proficiency checks work.
simple_melee_weapons = tuple(
    cls
    for cls in _generated.values()
    if issubclass(cls, SimpleWeapon) and issubclass(cls, MeleeWeapon)
)
simple_ranged_weapons = tuple(
    cls
    for cls in _generated.values()
    if issubclass(cls, SimpleWeapon) and issubclass(cls, RangedWeapon)
)
simple_weapons = simple_melee_weapons + simple_ranged_weapons

martial_melee_weapons = tuple(
    cls
    for cls in _generated.values()
    if issubclass(cls, MartialWeapon) and issubclass(cls, MeleeWeapon)
)
martial_ranged_weapons = tuple(
    cls
    for cls in _generated.values()
    if issubclass(cls, MartialWeapon) and issubclass(cls, RangedWeapon)
)
martial_weapons = martial_melee_weapons + martial_ranged_weapons

_MONK_WEAPON_NAMES = frozenset(
    (
        "Shortsword",
        "Club",
        "Dagger",
        "Handaxe",
        "Javelin",
        "LightHammer",
        "Mace",
        "Quarterstaff",
        "Sickle",
        "Spear",
        "SunBolt",
    )
)
monk_weapons = (Unarmed,) + tuple(
    cls for name, cls in _generated.items() if name in _MONK_WEAPON_NAMES
)

firearms = (Firearm,) + tuple(cls for cls in _generated.values() if issubclass(cls, Firearm))
