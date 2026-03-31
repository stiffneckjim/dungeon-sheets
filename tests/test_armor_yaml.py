"""Tests for YAML-driven armor loading."""

import unittest

from dungeonsheets import armor
from dungeonsheets.armor import (
    Armor,
    ChainMail,
    HeavyArmor,
    LeatherArmor,
    LightArmor,
    MediumArmor,
    PlateMail,
    ScaleMail,
)
from dungeonsheets.content_registry import default_content_registry


class TestArmorYamlLoading(unittest.TestCase):
    """Verify that armor classes are loaded correctly from armor.yaml."""

    # ------------------------------------------------------------------
    # Light armor
    # ------------------------------------------------------------------

    def test_leather_armor_base_ac(self):
        self.assertEqual(LeatherArmor.base_armor_class, 11)

    def test_leather_armor_type(self):
        self.assertIsSubclass(LeatherArmor, LightArmor)

    def test_leather_armor_no_stealth_disadvantage(self):
        self.assertFalse(LeatherArmor.stealth_disadvantage)

    def test_leather_armor_unlimited_dex(self):
        self.assertIsNone(LeatherArmor.dexterity_mod_max)

    def test_leather_armor_weight(self):
        self.assertEqual(LeatherArmor.weight, 10)

    def test_leather_armor_cost(self):
        self.assertEqual(LeatherArmor.cost, "10 gp")

    def test_padded_armor_stealth_disadvantage(self):
        from dungeonsheets.armor import PaddedArmor

        self.assertTrue(PaddedArmor.stealth_disadvantage)
        self.assertIsSubclass(PaddedArmor, LightArmor)

    def test_studded_leather_base_ac(self):
        from dungeonsheets.armor import StuddedLeatherArmor

        self.assertEqual(StuddedLeatherArmor.base_armor_class, 12)

    # ------------------------------------------------------------------
    # Medium armor
    # ------------------------------------------------------------------

    def test_scale_mail_is_medium(self):
        self.assertIsSubclass(ScaleMail, MediumArmor)

    def test_scale_mail_dex_cap(self):
        self.assertEqual(ScaleMail.dexterity_mod_max, 2)

    def test_scale_mail_stealth_disadvantage(self):
        self.assertTrue(ScaleMail.stealth_disadvantage)

    def test_breastplate_base_ac(self):
        from dungeonsheets.armor import Breastplate

        self.assertEqual(Breastplate.base_armor_class, 14)
        self.assertFalse(Breastplate.stealth_disadvantage)

    # ------------------------------------------------------------------
    # Heavy armor
    # ------------------------------------------------------------------

    def test_chain_mail_is_heavy(self):
        self.assertIsSubclass(ChainMail, HeavyArmor)

    def test_chain_mail_base_ac(self):
        self.assertEqual(ChainMail.base_armor_class, 16)

    def test_chain_mail_strength_required(self):
        self.assertEqual(ChainMail.strength_required, 13)

    def test_chain_mail_stealth_disadvantage(self):
        self.assertTrue(ChainMail.stealth_disadvantage)

    def test_heavy_armor_no_dex_applied(self):
        self.assertFalse(ChainMail.dexterity_applied)

    def test_plate_mail_base_ac(self):
        self.assertEqual(PlateMail.base_armor_class, 18)

    def test_plate_mail_strength_required(self):
        self.assertEqual(PlateMail.strength_required, 15)

    # ------------------------------------------------------------------
    # Custom armor
    # ------------------------------------------------------------------

    def test_elven_chain_loaded(self):
        from dungeonsheets.armor import ElvenChain

        self.assertIsSubclass(ElvenChain, MediumArmor)
        self.assertEqual(ElvenChain.base_armor_class, 14)
        self.assertEqual(ElvenChain.dexterity_mod_max, 2)

    # ------------------------------------------------------------------
    # Base-class inheritance
    # ------------------------------------------------------------------

    def test_all_yaml_armors_are_armor_subclasses(self):
        for armor_cls in armor.all_armors:
            with self.subTest(armor=armor_cls.__name__):
                self.assertTrue(issubclass(armor_cls, Armor))

    def test_data_source_attribute(self):
        self.assertEqual(LeatherArmor.data_source, "yaml")
        self.assertEqual(ChainMail.data_source, "yaml")

    # ------------------------------------------------------------------
    # Content registry
    # ------------------------------------------------------------------

    def test_registry_resolves_leather_armor(self):
        result = default_content_registry.findattr("leather_armor", valid_classes=[Armor])
        self.assertIs(result, LeatherArmor)

    def test_registry_resolves_chain_mail(self):
        result = default_content_registry.findattr("chain_mail", valid_classes=[Armor])
        self.assertIs(result, ChainMail)

    def test_registry_resolves_plate_mail(self):
        result = default_content_registry.findattr("plate_mail", valid_classes=[Armor])
        self.assertIs(result, PlateMail)

    # ------------------------------------------------------------------
    # all_armors list completeness
    # ------------------------------------------------------------------

    def test_all_armors_list_not_empty(self):
        self.assertGreater(len(armor.all_armors), 0)

    def test_all_armors_contains_expected_entries(self):
        from dungeonsheets.armor import (
            Breastplate,
            ChainShirt,
            HalfPlate,
            HideArmor,
            PaddedArmor,
            RingMail,
            SplintArmor,
            StuddedLeatherArmor,
        )

        expected = {
            PaddedArmor,
            LeatherArmor,
            StuddedLeatherArmor,
            HideArmor,
            ChainShirt,
            ScaleMail,
            Breastplate,
            HalfPlate,
            RingMail,
            ChainMail,
            SplintArmor,
            PlateMail,
        }
        self.assertEqual(set(armor.all_armors), expected)


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def assertIsSubclass(self, sub, parent):
    """Convenience so we can call self.assertIsSubclass."""
    self.assertTrue(
        issubclass(sub, parent),
        f"{sub.__name__} is not a subclass of {parent.__name__}",
    )


# Monkey-patch onto TestCase so the self.assertIsSubclass calls work
unittest.TestCase.assertIsSubclass = assertIsSubclass


if __name__ == "__main__":
    unittest.main()
