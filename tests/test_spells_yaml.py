from unittest import TestCase

from dungeonsheets import spells
from dungeonsheets.content_registry import find_content


class TestYamlBackedSpells(TestCase):
    """Verify that selected spells can be loaded from YAML."""

    def test_magic_missile_loaded_from_yaml(self):
        """Magic Missile should resolve to the YAML-backed spell class."""
        self.assertEqual(spells.MagicMissile.data_source, "yaml")
        self.assertEqual(spells.MagicMissile.level, 1)
        self.assertEqual(spells.MagicMissile.classes, ("Sorcerer", "Wizard"))

    def test_fireball_loaded_from_yaml(self):
        """Fireball should resolve to the YAML-backed spell class."""
        self.assertEqual(spells.Fireball.data_source, "yaml")
        self.assertEqual(spells.Fireball.level, 3)
        self.assertEqual(spells.Fireball.casting_range, "150 feet")

    def test_shield_loaded_from_yaml(self):
        """Shield should resolve to the YAML-backed spell class."""
        self.assertEqual(spells.Shield.data_source, "yaml")
        self.assertEqual(spells.Shield.magic_school, "Abjuration")
        self.assertEqual(spells.Shield.classes, ("Sorcerer", "Wizard"))

    def test_registry_finds_yaml_spell(self):
        """Content registry lookups should resolve YAML-backed spells."""
        shield_cls = find_content("shield", valid_classes=[spells.Spell])
        self.assertIs(shield_cls, spells.Shield)

    def test_mage_armor_loaded_from_yaml(self):
        """Mage Armor should now resolve to the YAML-backed spell class."""
        self.assertEqual(spells.MageArmor.data_source, "yaml")
        self.assertEqual(spells.MageArmor.level, 1)
