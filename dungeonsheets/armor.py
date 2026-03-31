from pathlib import Path

from dungeonsheets.content_registry import default_content_registry
from dungeonsheets.yaml_content import load_yaml_armor_classes

default_content_registry.add_module(__name__)


class Shield:
    """A shield that can be worn on one hand."""

    name = "Shield"
    cost = "10 gp"
    base_armor_class = 2
    weight = 6  # In lbs

    def __str__(self):
        return self.name

    def __repr__(self):
        return '"{:s}"'.format(self.name)

    @classmethod
    def improved_version(cls, bonus):
        bonus = int(bonus)

        class NewShield(cls):
            name = f"+{bonus} " + cls.name
            base_armor_class = cls.base_armor_class + bonus

        return NewShield


class WoodenShield(Shield):
    name = "Wooden shield"


class ShieldOfFaces(Shield):
    name = "Shield +1"
    base_armor_class = 3


class NoShield(Shield):
    """If a character is carrying no shield."""

    name = "No shield"
    cost = "0"
    base_armor_class = 0

    def __str__(self):
        return self.name


class Armor:
    """A piece of armor that can be worn.

    Attributes
    ----------
    name : str
      Human-readable name for this armor.
    cost : str
      Cost and currency for this armor.
    base_armor_class : int
      Armor class granted before modifiers.
    dexterity_mod_max : int
      How much dexterity can the user contribute. ``0`` for no
      dexterity modifier, ``None`` for unlimited dexterity modifier.
    strength_required : int
      Minimum strength needed to use this armor properly.
    stealth_disadvantage : bool
      If true, the armor causes disadvantage on stealth rolls.
    weight_class : str
      light, medium, or heavy
    weight : int
      In lbs.

    """

    name = "Unknown Armor"
    cost = "0 gp"
    base_armor_class = 10
    dexterity_mod_max = None
    dexterity_applied = True
    strength_required = None
    stealth_disadvantage = False
    weight = 0  # In lbs

    def __str__(self):
        return self.name

    def __repr__(self):
        return '"{:s}"'.format(self.name)

    @classmethod
    def improved_version(cls, bonus):
        bonus = int(bonus)

        class NewArmor(cls):
            name = f"+{bonus} " + cls.name
            base_armor_class = cls.base_armor_class + bonus

        return NewArmor


class NoArmor(Armor):
    name = "No Armor"


class LightArmor(Armor):
    name = "Light Armor"


class MediumArmor(Armor):
    name = "Medium Armor"


class HeavyArmor(Armor):
    name = "Heavy Armor"
    dexterity_applied = False


# ---------------------------------------------------------------------------
# Load all concrete armor definitions from YAML
# ---------------------------------------------------------------------------
_yaml_armors = load_yaml_armor_classes(
    Path(__file__).with_name("data") / "armor.yaml",
    Armor,
    type_map={
        "light": LightArmor,
        "medium": MediumArmor,
        "heavy": HeavyArmor,
    },
    module=__name__,
)
globals().update(_yaml_armors)

light_armors = [_yaml_armors[n] for n in ("PaddedArmor", "LeatherArmor", "StuddedLeatherArmor")]
medium_armors = [
    _yaml_armors[n] for n in ("HideArmor", "ChainShirt", "ScaleMail", "Breastplate", "HalfPlate")
]
heavy_armors = [_yaml_armors[n] for n in ("RingMail", "ChainMail", "SplintArmor", "PlateMail")]
all_armors = light_armors + medium_armors + heavy_armors
