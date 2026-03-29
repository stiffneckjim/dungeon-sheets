"""Tests for Phase 3 effect-based magic items: potions and charged staffs."""

import unittest

from dungeonsheets import magic_items
from dungeonsheets.content_registry import find_content


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
