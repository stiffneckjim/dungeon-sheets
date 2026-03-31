from unittest import TestCase

from dungeonsheets import magic_items
from dungeonsheets.content_registry import find_content


class TestYamlBackedMagicItems(TestCase):
    """Verify that selected magic items can be loaded from YAML."""

    def test_scroll_of_shield_loaded_from_yaml(self):
        """Scroll of Shield should resolve to the YAML-backed item class."""
        self.assertEqual(magic_items.ScrollOfShield.data_source, "yaml")
        self.assertEqual(magic_items.ScrollOfShield.linked_spells, ("shield",))

        item = magic_items.ScrollOfShield()
        self.assertEqual(item.granted_spell_names, ("shield",))

    def test_potion_of_healing_loaded_from_yaml(self):
        """Potion of Healing should expose passive effects from YAML attributes."""
        self.assertEqual(magic_items.PotionOfHealing.data_source, "yaml")

        item = magic_items.PotionOfHealing()
        passive_effects = [e for e in item.all_effects if isinstance(e, magic_items.PassiveEffect)]
        self.assertEqual(len(passive_effects), 1)
        self.assertEqual(passive_effects[0].bonus_value, 10)

    def test_staff_of_spells_charge_pool_from_yaml(self):
        """StaffOfSpells should expose charge pool metadata as ChargePoolEffect."""
        self.assertEqual(magic_items.StaffOfSpells.data_source, "yaml")

        item = magic_items.StaffOfSpells()
        charge_effects = [
            e for e in item.all_effects if isinstance(e, magic_items.ChargePoolEffect)
        ]
        self.assertEqual(len(charge_effects), 1)
        self.assertEqual(charge_effects[0].max_charges, 50)
        self.assertEqual(charge_effects[0].recharge_rule, "4d6 + 2 at dawn")

    def test_javelin_weapon_bonuses_from_yaml(self):
        """Javelin of Lightning should keep weapon bonus behavior via YAML."""
        self.assertEqual(magic_items.JavelinOfLightning.data_source, "yaml")

        item = magic_items.JavelinOfLightning()
        self.assertEqual(item.weapon_attack_bonus_total(), 1)
        self.assertEqual(item.weapon_damage_bonus_total(), 1)

    def test_registry_finds_yaml_items(self):
        """Registry lookups should resolve YAML-backed magic item classes."""
        shield_scroll_cls = find_content("scroll of shield")
        cloak_cls = find_content("cloak of protection")

        self.assertIs(shield_scroll_cls, magic_items.ScrollOfShield)
        self.assertIs(cloak_cls, magic_items.CloakOfProtection)

    def test_all_items_now_use_yaml(self):
        """All items should now come from YAML definitions."""
        self.assertEqual(magic_items.StaffOfTheAdder.data_source, "yaml")
        self.assertEqual(magic_items.StaffOfTheAdder.rarity, "Uncommon")
