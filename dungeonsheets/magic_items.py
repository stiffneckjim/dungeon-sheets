from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Sequence

from dungeonsheets.content_registry import default_content_registry
from dungeonsheets.yaml_content import load_yaml_magic_item_classes

default_content_registry.add_module(__name__)


@dataclass(frozen=True)
class MagicItemForm:
    """Describes what form a magic item takes."""

    kind: str = "wondrous"
    base_item: str = ""
    rarity: str = ""
    requires_attunement: bool = False
    is_consumable: bool = False


@dataclass(frozen=True)
class MagicItemEffect:
    """Marker base type for composable item effects."""


@dataclass(frozen=True)
class ArmorClassBonusEffect(MagicItemEffect):
    """An effect that grants a bonus to Armor Class.

    Attributes
    ----------
    amount : int
        The AC bonus provided by this effect.
    """

    amount: int = 0


@dataclass(frozen=True)
class SavingThrowBonusEffect(MagicItemEffect):
    """An effect that grants a bonus to saving throws.

    Attributes
    ----------
    all : int
        A bonus applied to all saving throws if no ability-specific bonus exists.
    strength, dexterity, constitution, intelligence, wisdom, charisma : Optional[int]
        Ability-specific saving throw bonuses. If None, the 'all' bonus is used.
    """

    all: int = 0
    strength: Optional[int] = None
    dexterity: Optional[int] = None
    constitution: Optional[int] = None
    intelligence: Optional[int] = None
    wisdom: Optional[int] = None
    charisma: Optional[int] = None

    def bonus(self, ability: str = "all") -> int:
        """Get the saving throw bonus for a specific ability.

        Parameters
        ----------
        ability : str
            The ability name (e.g., "strength", "dexterity"). Defaults to "all".

        Returns
        -------
        int
            The bonus for the specified ability, or the 'all' bonus if ability-specific
            bonus is None.
        """
        val = getattr(self, ability)
        if val is None:
            return self.all
        return val


@dataclass(frozen=True)
class SpellGrantedEffect(MagicItemEffect):
    """An effect that grants access to a spell.

    Attributes
    ----------
    spell : str
        The name of the spell granted by this effect.
    notes : str
        Optional notes about the spell granting (e.g., casting limits).
    uses_charges : bool
        Whether this spell uses charges from the item.
    charges_cost : int
        The number of charges required to cast this spell.
    """

    spell: str
    notes: str = ""
    uses_charges: bool = False
    charges_cost: int = 0


@dataclass(frozen=True)
class ChargePoolEffect(MagicItemEffect):
    """An effect that provides a pool of charges to an item.

    Attributes
    ----------
    max_charges : int
        The maximum number of charges this item can hold.
    recharge_rule : str
        Description of how charges recharge (e.g., "1d6 at dawn").
    """

    max_charges: int
    recharge_rule: str = ""


@dataclass(frozen=True)
class WeaponModifierEffect(MagicItemEffect):
    """An effect that modifies weapon attack or damage rolls.

    This effect is used for magic weapons that grant bonuses to attack rolls,
    damage rolls, or both. It enables the composable effect model for weapons.

    Attributes
    ----------
    attack_bonus : int
        Bonus applied to attack rolls with this weapon.
    damage_bonus : int
        Bonus applied to damage rolls with this weapon.
    """

    attack_bonus: int = 0
    damage_bonus: int = 0


@dataclass(frozen=True)
class PassiveEffect(MagicItemEffect):
    """An effect that provides a passive ability or property.

    This is a flexible effect for describing passive properties that don't
    fit into other specific categories (e.g., potion healing amounts, damage
    resistances, breathing underwater, etc.).

    Attributes
    ----------
    description : str
        A human-readable description of the passive effect.
    bonus_value : int
        An optional numeric value associated with the effect (e.g., healing
        amount, damage reduction, hours of duration).
    """

    description: str
    bonus_value: int = 0


class MagicItem:
    """Generic Magic Item. Add description here.

    Should be subclassed in order to create magic items.

    Saving throw bonuses should be implemented using the various
    *st_bonus_<ability>* attributes. *st_bonus_all* will be used if
    the ST bonus for the ability in question is not specified on the
    subclass.

    Attributes
    ==========
    name
      Human-readable name for this magic item.
    requires_attunement
      If true, this magic item requires attunement in order to achieve
      the benefits.
    rarity
      The rarity of this magic item, as a human-readable string.
    item_type
      The type of item: "armor", "weapon", etc.
    ac_bonus
      Provides an armor class bonus to any creature equipping this item.
    st_bonus_all
      A bonus to all savings throws to any creature equipping this item.
    st_bonus_strength
      A bonus to strength saving throws to any creature equipping this item.
    st_bonus_dexterity
      A bonus to dexterity saving throws to any creature equipping this item.
    st_bonus_constitution
      A bonus to constitution saving throws to any creature equipping this item.
    st_bonus_intelligence
      A bonus to intelligence saving throws to any creature equipping this item.
    st_bonus_wisdom
      A bonus to wisdom saving throws to any creature equipping this item.
    st_bonus_charisma
      A bonus to charisma saving throws to any creature equipping this item.
        linked_spells
            Spell names linked to this item. Used to model effects like
            spell scrolls and other spell-granting items.

    """

    # Magic-item specific attributes
    name: str = "Generic Magic Item"
    requires_attunement: bool = False
    # needs_implementation: bool = False
    rarity: str = ""
    item_type: str = ""
    # Bonuses
    ac_bonus: int = 0
    st_bonus_all: int = 0
    st_bonus_strength: Optional[int] = None
    st_bonus_dexterity: Optional[int] = None
    st_bonus_constitution: Optional[int] = None
    st_bonus_intelligence: Optional[int] = None
    st_bonus_wisdom: Optional[int] = None
    st_bonus_charisma: Optional[int] = None
    # Weapon bonuses (for magic weapons)
    weapon_attack_bonus: int = 0
    weapon_damage_bonus: int = 0
    # Passive effects (for potions, consumables, passive bonuses)
    passive_effect_description: str = ""
    passive_effect_value: int = 0
    # Charge pool metadata
    charge_pool_max: int = 0
    charge_recharge_rule: str = ""
    linked_spells: Sequence[str] = tuple()
    form: Optional[MagicItemForm] = None
    effects: Sequence[MagicItemEffect] = tuple()

    def __init__(
        self,
        wielder=None,
        form: Optional[MagicItemForm] = None,
        effects: Optional[Sequence[MagicItemEffect]] = None,
    ):
        self.wielder = wielder
        self.form = form or self.form or self._legacy_form()
        self._effects = list(effects if effects is not None else self.effects)
        self._effects.extend(self._legacy_effects())

    def __str__(self):
        return self.name

    def __repr__(self):
        return '<MagicItem: "{:s}">'.format(str(self))

    def _ensure_effect_state(self):
        """Lazily initialize effect-related state for mixin compatibility.

        Some homebrew classes use multiple inheritance where another base class
        provides ``__init__`` and ``MagicItem.__init__`` is not called.
        Initialize ``form`` and ``_effects`` on first use so those classes still
        behave as magic items.
        """
        if not hasattr(self, "form") or self.form is None:
            self.form = self._legacy_form()

        if not hasattr(self, "_effects"):
            self._effects = list(self.effects)
            self._effects.extend(self._legacy_effects())

    def _legacy_form(self) -> MagicItemForm:
        """Generate a MagicItemForm from legacy class attributes.

        Returns
        -------
        MagicItemForm
            A form describing the item's basic properties derived from
            legacy class attributes.
        """
        return MagicItemForm(
            kind=(self.item_type or "wondrous").lower(),
            base_item=self.item_type,
            rarity=self.rarity,
            requires_attunement=self.requires_attunement,
            is_consumable=(self.item_type or "").lower() in {"consumable", "potion", "scroll"},
        )

    def _legacy_effects(self) -> list[MagicItemEffect]:
        """Generate MagicItemEffect objects from legacy class attributes.

        Converts traditional ac_bonus, st_bonus_*, weapon bonuses, passive traits,
        charge metadata, and linked_spells attributes into corresponding effect
        objects for backward compatibility.

        Returns
        -------
        list[MagicItemEffect]
            A list of effects derived from legacy attributes.
        """
        effects: list[MagicItemEffect] = []
        if self.ac_bonus:
            effects.append(ArmorClassBonusEffect(amount=self.ac_bonus))

        st_effect = SavingThrowBonusEffect(
            all=self.st_bonus_all,
            strength=self.st_bonus_strength,
            dexterity=self.st_bonus_dexterity,
            constitution=self.st_bonus_constitution,
            intelligence=self.st_bonus_intelligence,
            wisdom=self.st_bonus_wisdom,
            charisma=self.st_bonus_charisma,
        )
        has_st_bonus = any(
            val is not None and val != 0
            for val in (
                st_effect.all,
                st_effect.strength,
                st_effect.dexterity,
                st_effect.constitution,
                st_effect.intelligence,
                st_effect.wisdom,
                st_effect.charisma,
            )
        )
        if has_st_bonus:
            effects.append(st_effect)

        # Convert weapon bonuses to effects if this is a magic weapon
        if self.weapon_attack_bonus or self.weapon_damage_bonus:
            effects.append(
                WeaponModifierEffect(
                    attack_bonus=self.weapon_attack_bonus,
                    damage_bonus=self.weapon_damage_bonus,
                )
            )

        for spell_name in self.linked_spells:
            effects.append(SpellGrantedEffect(spell=spell_name))

        # Convert passive effects if defined
        if self.passive_effect_description:
            effects.append(
                PassiveEffect(
                    description=self.passive_effect_description,
                    bonus_value=self.passive_effect_value,
                )
            )

        if self.charge_pool_max:
            effects.append(
                ChargePoolEffect(
                    max_charges=self.charge_pool_max,
                    recharge_rule=self.charge_recharge_rule,
                )
            )
        return effects

    @property
    def all_effects(self) -> tuple[MagicItemEffect, ...]:
        """Get all effects (both new and legacy-converted) for this item.

        Returns
        -------
        tuple[MagicItemEffect, ...]
            A tuple of all composable effects for this magic item.
        """
        self._ensure_effect_state()
        return tuple(self._effects)

    @property
    def granted_spell_names(self) -> tuple[str, ...]:
        """Get the names of all spells granted by this item.

        Returns
        -------
        tuple[str, ...]
            A tuple of spell names from all SpellGrantedEffect objects.
        """
        self._ensure_effect_state()
        spell_effects = [e.spell for e in self._effects if isinstance(e, SpellGrantedEffect)]
        return tuple(spell_effects)

    def granted_spell_classes(self):
        """Resolve granted spell names to their Spell class definitions.

        Returns
        -------
        tuple[type[Spell], ...]
            A tuple of Spell classes corresponding to granted_spell_names.
        """
        from dungeonsheets import spells
        from dungeonsheets.content_registry import find_content

        return tuple(
            find_content(name, valid_classes=[spells.Spell]) for name in self.granted_spell_names
        )

    def ac_bonus_total(self) -> int:
        """Calculate the total armor class bonus from all AC effects.

        Returns
        -------
        int
            The sum of all ArmorClassBonusEffect amounts.
        """
        self._ensure_effect_state()
        return sum(
            effect.amount for effect in self._effects if isinstance(effect, ArmorClassBonusEffect)
        )

    def st_bonus(self, ability: Optional[str] = "all") -> int:
        """Get the total saving throw bonus for a specific ability.

        Parameters
        ----------
        ability : Optional[str]
            The ability for which to retrieve the saving throw bonus.
            Defaults to "all".

        Returns
        -------
        int
            The total saving throw bonus from all effects plus legacy attributes.
        """
        self._ensure_effect_state()
        ability_name = ability or "all"
        effects = [e for e in self._effects if isinstance(e, SavingThrowBonusEffect)]
        if len(effects) == 0:
            bonus = getattr(self, f"st_bonus_{ability_name}")
            if bonus is None:
                bonus = self.st_bonus_all
            return bonus
        return sum(effect.bonus(ability=ability_name) for effect in effects)

    def weapon_attack_bonus_total(self) -> int:
        """Calculate the total attack bonus from all weapon modifier effects.

        Returns
        -------
        int
            The sum of all WeaponModifierEffect attack_bonus values.
        """
        self._ensure_effect_state()
        return sum(
            effect.attack_bonus
            for effect in self._effects
            if isinstance(effect, WeaponModifierEffect)
        )

    def weapon_damage_bonus_total(self) -> int:
        """Calculate the total damage bonus from all weapon modifier effects.

        Returns
        -------
        int
            The sum of all WeaponModifierEffect damage_bonus values.
        """
        self._ensure_effect_state()
        return sum(
            effect.damage_bonus
            for effect in self._effects
            if isinstance(effect, WeaponModifierEffect)
        )


class SpellScroll(MagicItem):
    """A generic scroll that grants access to a spell.

    Spell scrolls are consumable items that provide temporary access to spells.
    Subclass this with linked_spells to create specific scroll types.

    Attributes
    ----------
    item_type : str
        Set to "Scroll".
    form : MagicItemForm
        Describes the scroll form as a consumable item.
    """

    item_type = "Scroll"
    form = MagicItemForm(kind="scroll", base_item="Scroll", is_consumable=True)

    @classmethod
    def scroll_for(cls, spell_name: str) -> type:
        """Dynamically create a SpellScroll subclass for any spell by name.

        Analogous to ``Weapon.improved_version()``: resolves the spell name
        via the content registry to validate it exists, then returns a new
        ``SpellScroll`` subclass with that spell linked.

        Parameters
        ----------
        spell_name : str
            The spell name as it would appear in a character file
            (e.g. ``"fireball"``, ``"charm person"``).

        Returns
        -------
        type[SpellScroll]
            A ``SpellScroll`` subclass whose ``linked_spells`` contains
            *spell_name* and whose ``name`` is ``"Scroll of <Title>"``.  The
            spell is validated via ``find_content`` so unknown names still
            raise ``ContentNotFound``.
        """
        from dungeonsheets import spells as _spells
        from dungeonsheets.content_registry import find_content

        # Validate the spell exists — raises ContentNotFound for unknown spells
        find_content(spell_name, valid_classes=[_spells.Spell])

        title = spell_name.replace("_", " ").title()
        camel = "".join(
            s.capitalize() for s in spell_name.replace("-", " ").replace("_", " ").split()
        )

        new_cls = type(
            f"ScrollOf{camel}",
            (cls,),
            {
                "name": f"Scroll of {title}",
                "linked_spells": (spell_name,),
            },
        )
        return new_cls


globals().update(
    load_yaml_magic_item_classes(
        (
            Path(__file__).with_name("data").joinpath("magic_items")
            if Path(__file__).with_name("data").joinpath("magic_items").is_dir()
            else Path(__file__).with_name("data").joinpath("magic_items.yaml")
        ),
        MagicItem,
        module=__name__,
    )
)
