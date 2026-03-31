"""Tests for weapons loaded from YAML."""

import unittest

from dungeonsheets import weapons
from dungeonsheets.content_registry import find_content
from dungeonsheets.weapons import (
    Firearm,
    MartialWeapon,
    MeleeWeapon,
    RangedWeapon,
    SimpleWeapon,
    Unarmed,
    Weapon,
)


class TestYamlWeaponAttributes(unittest.TestCase):
    """Verify that representative weapons carry the correct YAML-sourced attributes."""

    def test_shortsword_attributes(self):
        self.assertEqual(weapons.Shortsword.data_source, "yaml")
        self.assertEqual(weapons.Shortsword.name, "Shortsword")
        self.assertEqual(weapons.Shortsword.base_damage, "1d6")
        self.assertEqual(weapons.Shortsword.damage_type, "p")
        self.assertEqual(weapons.Shortsword.weight, 2)
        self.assertEqual(weapons.Shortsword.cost, "10 gp")
        self.assertTrue(weapons.Shortsword.is_finesse)
        self.assertEqual(weapons.Shortsword.ability, "strength")

    def test_longbow_attributes(self):
        self.assertEqual(weapons.Longbow.data_source, "yaml")
        self.assertEqual(weapons.Longbow.name, "Longbow")
        self.assertEqual(weapons.Longbow.base_damage, "1d8")
        self.assertEqual(weapons.Longbow.ability, "dexterity")

    def test_dagger_is_finesse(self):
        self.assertTrue(weapons.Dagger.is_finesse)
        self.assertEqual(weapons.Dagger.damage_type, "p")

    def test_net_has_dash_damage(self):
        self.assertEqual(weapons.Net.base_damage, "-")

    def test_blowgun_damage_is_string_one(self):
        self.assertEqual(weapons.Blowgun.base_damage, "1")

    def test_musket_cost_normalised(self):
        self.assertEqual(weapons.Musket.cost, "300 gp")

    def test_heavy_punch_bonuses(self):
        self.assertEqual(weapons.HeavyPunch.damage_bonus, 10)
        self.assertEqual(weapons.HeavyPunch.attack_bonus, -5)


class TestYamlWeaponInheritance(unittest.TestCase):
    """Verify that YAML-loaded weapons inherit the correct category base classes."""

    def test_shortsword_is_martial_melee(self):
        self.assertTrue(issubclass(weapons.Shortsword, MartialWeapon))
        self.assertTrue(issubclass(weapons.Shortsword, MeleeWeapon))

    def test_longbow_is_martial_ranged(self):
        self.assertTrue(issubclass(weapons.Longbow, MartialWeapon))
        self.assertTrue(issubclass(weapons.Longbow, RangedWeapon))

    def test_club_is_simple_melee(self):
        self.assertTrue(issubclass(weapons.Club, SimpleWeapon))
        self.assertTrue(issubclass(weapons.Club, MeleeWeapon))

    def test_shortbow_is_simple_ranged(self):
        self.assertTrue(issubclass(weapons.Shortbow, SimpleWeapon))
        self.assertTrue(issubclass(weapons.Shortbow, RangedWeapon))

    def test_pistol_is_firearm(self):
        self.assertTrue(issubclass(weapons.Pistol, Firearm))

    def test_bite_is_unarmed(self):
        self.assertTrue(issubclass(weapons.Bite, Unarmed))

    def test_sun_bolt_is_ranged_weapon(self):
        self.assertTrue(issubclass(weapons.SunBolt, RangedWeapon))

    def test_all_yaml_weapons_are_weapons(self):
        for cls_name in (
            "Club", "Dagger", "Greatclub", "Handaxe", "Javelin", "LightHammer", "Mace",
            "Quarterstaff", "Sickle", "Spear", "LightCrossbow", "Dart", "Shortbow", "Sling",
            "Battleaxe", "Flail", "Glaive", "Greataxe", "Greatsword", "Halberd", "Lance",
            "Longsword", "Maul", "Morningstar", "Pike", "Rapier", "Scimitar", "Shortsword",
            "ThrowingHammer", "Trident", "WarPick", "Warhammer", "Whip", "Blowgun",
            "HandCrossbow", "HeavyCrossbow", "Longbow", "Net", "SunBolt", "Blunderbuss",
            "Pistol", "Musket", "HeavyPunch", "Bite", "Talons", "Claws",
        ):
            cls = getattr(weapons, cls_name)
            self.assertTrue(
                issubclass(cls, Weapon),
                f"{cls_name} is not a subclass of Weapon",
            )


class TestYamlWeaponRegistry(unittest.TestCase):
    """Verify the content registry resolves YAML-loaded weapon names."""

    def test_registry_finds_shortsword(self):
        cls = find_content("shortsword")
        self.assertIs(cls, weapons.Shortsword)

    def test_registry_finds_longsword(self):
        cls = find_content("longsword")
        self.assertIs(cls, weapons.Longsword)

    def test_registry_finds_light_hammer(self):
        cls = find_content("light hammer")
        self.assertIs(cls, weapons.LightHammer)


class TestImprovedVersion(unittest.TestCase):
    """Verify improved_version() works on YAML-loaded weapons."""

    def test_improved_shortsword(self):
        PlusTwoShortsword = weapons.Shortsword.improved_version(2)
        self.assertEqual(PlusTwoShortsword.name, "+2 Shortsword")
        self.assertEqual(PlusTwoShortsword.attack_bonus, 2)
        self.assertEqual(PlusTwoShortsword.damage_bonus, 2)

    def test_improved_longsword_is_subclass(self):
        PlusOneLongsword = weapons.Longsword.improved_version(1)
        self.assertTrue(issubclass(PlusOneLongsword, weapons.Longsword))
        self.assertTrue(issubclass(PlusOneLongsword, Weapon))

    def test_improved_weapon_damage_string(self):
        PlusTwoDagger = weapons.Dagger.improved_version(2)
        instance = PlusTwoDagger(wielder=None)
        self.assertEqual(instance.damage, "1d4+2")


class TestWeaponLists(unittest.TestCase):
    """Verify the pre-built weapon category tuples contain the expected classes."""

    def test_simple_melee_weapons(self):
        self.assertIn(weapons.Club, weapons.simple_melee_weapons)
        self.assertIn(weapons.Spear, weapons.simple_melee_weapons)

    def test_martial_melee_weapons(self):
        self.assertIn(weapons.Longsword, weapons.martial_melee_weapons)
        self.assertIn(weapons.Shortsword, weapons.martial_melee_weapons)

    def test_firearms_tuple(self):
        self.assertIn(weapons.Blunderbuss, weapons.firearms)
        self.assertIn(weapons.Pistol, weapons.firearms)
        self.assertIn(weapons.Musket, weapons.firearms)

    def test_monk_weapons_includes_sun_bolt(self):
        self.assertIn(weapons.SunBolt, weapons.monk_weapons)