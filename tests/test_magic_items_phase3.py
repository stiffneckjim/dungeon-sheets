"""Tests for Phase 3 effect-based magic items: potions and charged staffs."""

import unittest

from dungeonsheets import magic_items, spells
from dungeonsheets.content_registry import find_content
from dungeonsheets.exceptions import ContentNotFound


class PhaseThreeItemTests(unittest.TestCase):
    """Test cases for Phase 3 item migrations using effect composition."""

    def test_potion_healing_passive_effect(self):
        """Verify that potions expose passive effects like healing.

        Potions should automatically expose their passive_effect_description
        and passive_effect_value as PassiveEffect objects in all_effects.
        """
        item = magic_items.PotionOfHealing()
        passive_effects = [e for e in item.all_effects if isinstance(e, magic_items.PassiveEffect)]
        self.assertEqual(len(passive_effects), 1)
        self.assertIn("2d4 + 2", passive_effects[0].description)
        self.assertEqual(passive_effects[0].bonus_value, 10)

    def test_staff_of_spells_grants_multiple_spells(self):
        """Verify that staffs can grant access to multiple spells.

        The StaffOfSpells item uses linked_spells to provide access to
        multiple spell definitions, exposing them through granted_spell_names
        and granted_spell_classes().
        """
        item_cls = find_content("staff of spells")
        self.assertIs(item_cls, magic_items.StaffOfSpells)
        item = item_cls()
        # Should have all four spells
        self.assertEqual(len(item.granted_spell_names), 4, msg="Staff should grant 4 spells")
        # Verify spell names
        self.assertIn("magic missile", item.granted_spell_names)
        self.assertIn("fireball", item.granted_spell_names)
        # Verify classes can be resolved
        spell_classes = item.granted_spell_classes()
        self.assertEqual(len(spell_classes), 4)

    def test_potion_of_healing_registration(self):
        """Verify that PotionOfHealing is registered and discoverable.

        Potions should be discoverable through the content registry like
        other magic items.
        """
        item_cls = find_content("potion of healing")
        self.assertIs(item_cls, magic_items.PotionOfHealing)
        item = item_cls()
        self.assertEqual(item.name, "Potion of Healing")
        self.assertEqual(item.rarity, "Common")
        self.assertEqual(item.item_type, "Potion")

    def test_staff_of_spells_registration(self):
        """Verify that StaffOfSpells is registered and discoverable."""
        item_cls = find_content("staff of spells")
        self.assertIs(item_cls, magic_items.StaffOfSpells)
        item = item_cls()
        self.assertEqual(item.name, "Staff of Spells")
        self.assertEqual(item.rarity, "Very Rare")
        self.assertTrue(item.requires_attunement)


class DynamicSpellScrollTests(unittest.TestCase):
    """Test dynamic creation of spell scrolls via 'scroll of <spell>' lookup."""

    def test_scroll_of_fireball_resolves_via_registry(self):
        """'scroll of fireball' should resolve to a SpellScroll for Fireball."""
        item_cls = find_content("scroll of fireball")
        self.assertTrue(issubclass(item_cls, magic_items.SpellScroll))
        item = item_cls()
        self.assertEqual(item.name, "Scroll of Fireball")
        self.assertIn("fireball", item.granted_spell_names)
        spell_classes = item.granted_spell_classes()
        self.assertEqual(len(spell_classes), 1)
        self.assertIs(spell_classes[0], spells.Fireball)

    def test_scroll_of_charm_person_resolves_via_registry(self):
        """'scroll of charm person' should resolve to a SpellScroll for Charm Person."""
        item_cls = find_content("scroll of charm person")
        self.assertTrue(issubclass(item_cls, magic_items.SpellScroll))
        item = item_cls()
        self.assertIn("charm person", item.granted_spell_names)
        spell_classes = item.granted_spell_classes()
        self.assertEqual(len(spell_classes), 1)
        self.assertIs(spell_classes[0], spells.CharmPerson)

    def test_scroll_is_consumable(self):
        """Dynamically created scrolls should be marked as consumable."""
        item_cls = find_content("scroll of fireball")
        item = item_cls()
        self.assertEqual(item.item_type, "Scroll")
        self.assertTrue(item.form.is_consumable)

    def test_scroll_for_unknown_spell_raises_content_not_found(self):
        """'scroll of notarealspell' should raise ContentNotFound."""
        with self.assertRaises(ContentNotFound):
            find_content("scroll of notarealspell")

    def test_scroll_for_classmethod_returns_subclass(self):
        """SpellScroll.scroll_for() returns a SpellScroll subclass with spell linked."""
        cls = magic_items.SpellScroll.scroll_for("magic missile")
        self.assertTrue(issubclass(cls, magic_items.SpellScroll))
        item = cls()
        self.assertIn("magic missile", item.granted_spell_names)
        self.assertEqual(item.name, "Scroll of Magic Missile")
