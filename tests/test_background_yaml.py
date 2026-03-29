from unittest import TestCase

from dungeonsheets import background, features
from dungeonsheets.content_registry import find_content

MIGRATED_BACKGROUND_CLASSES = (
    "Acolyte",
    "Charlatan",
    "Criminal",
    "Spy",
    "Entertainer",
    "Gladiator",
    "Farmer",
    "FolkHero",
    "GuildArtisan",
    "GuildMerchant",
    "Hermit",
    "Noble",
    "Knight",
    "Outlander",
    "RivalIntern",
    "Sage",
    "Sailor",
    "Pirate",
    "Soldier",
    "Urchin",
    "CityWatch",
    "ClanCrafter",
    "CloisteredScholar",
    "Courtier",
    "FactionAgent",
    "FarTraveler",
    "Inheritor",
    "KnightOfTheOrder",
    "MercenaryVeteran",
    "UrbanBountyHunter",
    "UthgardtTribeMember",
    "WaterdhavianNoble",
    "Faceless",
)


class TestYamlBackedBackgrounds(TestCase):
    """Verify that background definitions are loaded from YAML."""

    def test_acolyte_loaded_from_yaml(self):
        """Acolyte should resolve to the YAML-backed class definition."""
        self.assertEqual(background.Acolyte.data_source, "yaml")
        self.assertEqual(background.Acolyte.skill_proficiencies, ("insight", "religion"))
        self.assertEqual(background.Acolyte.languages, ("[choose one]", "[choose one]"))

        acolyte = background.Acolyte()
        self.assertEqual(len(acolyte.features), 1)
        self.assertIsInstance(acolyte.features[0], features.ShelterOfTheFaithful)

    def test_soldier_loaded_from_yaml(self):
        """Soldier should resolve to the YAML-backed class definition."""
        self.assertEqual(background.Soldier.data_source, "yaml")
        self.assertEqual(background.Soldier.skill_proficiencies, ("athletics", "intimidation"))

        soldier = background.Soldier()
        self.assertEqual(len(soldier.features), 1)
        self.assertIsInstance(soldier.features[0], features.MilitaryRank)

    def test_registry_finds_yaml_background(self):
        """Content registry lookups should continue to work for YAML-backed classes."""
        acolyte_cls = find_content("acolyte", valid_classes=[background.Background])
        soldier_cls = find_content("soldier", valid_classes=[background.Background])
        self.assertIs(acolyte_cls, background.Acolyte)
        self.assertIs(soldier_cls, background.Soldier)

    def test_all_backgrounds_are_loaded_from_yaml(self):
        """All migrated background classes should be marked as YAML-backed."""
        for class_name in MIGRATED_BACKGROUND_CLASSES:
            with self.subTest(class_name=class_name):
                cls = getattr(background, class_name)
                self.assertEqual(cls.data_source, "yaml")

    def test_uthgardt_background_uses_correct_skill_field(self):
        """YAML migration fixes the legacy typo on Uthgardt skill proficiencies."""
        cls = background.UthgardtTribeMember
        self.assertEqual(cls.skill_proficiencies, ("athletics", "survival"))
        self.assertFalse(hasattr(cls, "skill_profifiencies"))
