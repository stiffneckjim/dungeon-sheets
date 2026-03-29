"""
Unit tests for magic items in dungeonsheets. These tests cover the
functionality of the MagicItem base class, as well as specific magic items like
the Staff of the Adder and Javelin of Lightning.

The tests verify that saving throw bonuses are calculated correctly based on
item properties and character attributes, and that specific magic items are
properly registered in the content registry with their expected attributes.
"""

import unittest

from dungeonsheets import magic_items
from dungeonsheets.character import Character
from dungeonsheets.content_registry import find_content
from dungeonsheets.spells import Shield
from dungeonsheets.weapons import Weapon


class MyMagicItem(magic_items.MagicItem): ...


class MixinMagicWeapon(Weapon, magic_items.MagicItem):
    """Mixin class where Weapon.__init__ shadows MagicItem.__init__."""

    name = "Mixin Magic Weapon"


class MagicItemTests(unittest.TestCase):
    def test_st_bonus_all(self):
        char = Character()
        my_item = MyMagicItem(wielder=char)
        char.magic_items = [my_item]
        # Test an item that confers no saving throw bonus
        bonus = my_item.st_bonus()
        self.assertEqual(bonus, 0)
        # Now test with positive ST bonus
        my_item.st_bonus_all = 2
        bonus = my_item.st_bonus()
        self.assertEqual(bonus, 2)

    def test_st_bonus_by_ability(self):
        char = Character(strength=10)
        my_item = MyMagicItem(wielder=char)
        char.magic_items = [my_item]
        # Test an item with nonsense ability
        with self.assertRaises(AttributeError):
            my_item.st_bonus(ability="flight")
        # Test that the st_bonus_all is used if the specific ability is not listed
        my_item.st_bonus_all = 2
        bonus = my_item.st_bonus(ability="strength")
        self.assertEqual(bonus, 2)
        # Test a specific st_bonus
        my_item.st_bonus_strength = 3
        bonus = my_item.st_bonus(ability="strength")
        self.assertEqual(bonus, 3)

    def test_staff_of_the_adder_registration_and_attributes(self):
        item_cls = find_content("staff of the adder")
        self.assertIs(item_cls, magic_items.StaffOfTheAdder)

        item = item_cls()
        self.assertEqual(item.name, "Staff of the Adder")
        self.assertEqual(item.rarity, "Uncommon")
        self.assertTrue(item.requires_attunement)
        self.assertEqual(item.item_type, "Staff")

    def test_javelin_of_lightning_registration_and_attributes(self):
        item_cls = find_content("javelin of lightning")
        self.assertIs(item_cls, magic_items.JavelinOfLightning)

        item = item_cls()
        self.assertEqual(item.name, "Javelin of Lightning")
        self.assertEqual(item.rarity, "Uncommon")
        self.assertTrue(item.requires_attunement)
        self.assertEqual(item.item_type, "Weapon")

    def test_legacy_bonus_attrs_are_exposed_as_effects(self):
        """Verify that legacy ac_bonus and st_bonus_* attributes are exposed as effects.

        When a legacy magic item is instantiated, its ac_bonus and st_bonus_*
        attributes should be automatically converted to corresponding effect objects
        and exposed through the all_effects property.
        """
        item = magic_items.CloakOfProtection()
        ac_effects = [
            e for e in item.all_effects if isinstance(e, magic_items.ArmorClassBonusEffect)
        ]
        st_effects = [
            e for e in item.all_effects if isinstance(e, magic_items.SavingThrowBonusEffect)
        ]
        self.assertEqual(len(ac_effects), 1)
        self.assertEqual(ac_effects[0].amount, 1)
        self.assertEqual(len(st_effects), 1)
        self.assertEqual(st_effects[0].all, 1)

    def test_scroll_links_to_spell_definition(self):
        """Verify that spell scrolls resolve to their spell definitions.

        Spell scrolls should be discoverable through the content registry,
        expose their granted spells through granted_spell_names, and resolve
        those spell names to actual Spell class definitions via granted_spell_classes().
        """
        item_cls = find_content("scroll of shield")
        self.assertIs(item_cls, magic_items.ScrollOfShield)
        item = item_cls()
        self.assertEqual(item.granted_spell_names, ("shield",))
        spell_classes = item.granted_spell_classes()
        self.assertEqual(spell_classes, (Shield,))

    def test_weapon_bonuses_exposed_as_effects(self):
        """Verify that weapon bonuses are exposed as WeaponModifierEffect objects.

        When a magic weapon uses legacy weapon_attack_bonus and weapon_damage_bonus
        attributes, they should be automatically converted to WeaponModifierEffect
        and exposed through all_effects.
        """
        item = magic_items.JavelinOfLightning()
        weapon_effects = [
            e for e in item.all_effects if isinstance(e, magic_items.WeaponModifierEffect)
        ]
        self.assertEqual(len(weapon_effects), 1)
        self.assertEqual(weapon_effects[0].attack_bonus, 1)
        self.assertEqual(weapon_effects[0].damage_bonus, 1)

    def test_weapon_bonus_aggregation(self):
        """Verify that weapon bonuses are correctly aggregated from effects.

        The weapon_attack_bonus_total() and weapon_damage_bonus_total() methods
        should sum values from all WeaponModifierEffect objects.
        """
        item = magic_items.JavelinOfLightning()
        self.assertEqual(item.weapon_attack_bonus_total(), 1)
        self.assertEqual(item.weapon_damage_bonus_total(), 1)

    def test_mixin_magic_item_without_magicitem_init_is_safe(self):
        """Mixin items should lazily initialize magic item effect state."""
        item = MixinMagicWeapon()
        self.assertEqual(item.st_bonus("strength"), 0)
        self.assertEqual(item.ac_bonus_total(), 0)
        self.assertEqual(item.granted_spell_names, ())

    def test_st_bonus_allows_none_as_alias_for_all(self):
        """Passing None should behave the same as querying all saves."""
        item = MyMagicItem()
        item.st_bonus_all = 2
        self.assertEqual(item.st_bonus(None), 2)
