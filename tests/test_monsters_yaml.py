"""Tests for load_yaml_monster_classes() in yaml_content.py."""

import sys
import types
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from dungeonsheets.content_registry import ContentRegistry
from dungeonsheets.monsters.monsters import Monster
from dungeonsheets.yaml_content import load_yaml_monster_classes

_FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"
_MONSTERS_YAML = _FIXTURES_DIR / "monsters_test.yaml"


class TestLoadYamlMonsterClassesScalars(TestCase):
    """Verify scalar field mapping from YAML to generated monster classes."""

    @classmethod
    def setUpClass(cls):
        cls.classes = load_yaml_monster_classes(_MONSTERS_YAML, Monster)

    def test_returns_all_class_names(self):
        self.assertIn("TestGoblin", self.classes)
        self.assertIn("TestOgre", self.classes)
        self.assertIn("TestAncientDragon", self.classes)

    def test_classes_are_monster_subclasses(self):
        for name, cls in self.classes.items():
            with self.subTest(name=name):
                self.assertTrue(issubclass(cls, Monster))

    def test_data_source_is_yaml(self):
        for name, cls in self.classes.items():
            with self.subTest(name=name):
                self.assertEqual(cls.data_source, "yaml")

    def test_goblin_name(self):
        self.assertEqual(self.classes["TestGoblin"].name, "Goblin")

    def test_goblin_challenge_rating(self):
        self.assertEqual(self.classes["TestGoblin"].challenge_rating, 0.25)

    def test_goblin_armor_class(self):
        self.assertEqual(self.classes["TestGoblin"].armor_class, 15)

    def test_goblin_hp_max(self):
        self.assertEqual(self.classes["TestGoblin"].hp_max, 7)

    def test_goblin_speed(self):
        self.assertEqual(self.classes["TestGoblin"].speed, "30 ft.")

    def test_goblin_ability_scores(self):
        goblin = self.classes["TestGoblin"]()
        self.assertEqual(goblin.strength.value, 8)
        self.assertEqual(goblin.dexterity.value, 14)
        self.assertEqual(goblin.constitution.value, 10)
        self.assertEqual(goblin.intelligence.value, 10)
        self.assertEqual(goblin.wisdom.value, 8)
        self.assertEqual(goblin.charisma.value, 8)

    def test_goblin_skills(self):
        self.assertEqual(self.classes["TestGoblin"].skills, "Stealth +6")

    def test_goblin_senses(self):
        self.assertIn("Darkvision", self.classes["TestGoblin"].senses)

    def test_goblin_languages(self):
        self.assertIn("Goblin", self.classes["TestGoblin"].languages)

    def test_dragon_challenge_rating(self):
        self.assertEqual(self.classes["TestAncientDragon"].challenge_rating, 24)

    def test_dragon_saving_throws(self):
        self.assertIn("Con", self.classes["TestAncientDragon"].saving_throws)

    def test_dragon_damage_immunities(self):
        self.assertEqual(self.classes["TestAncientDragon"].damage_immunities, "fire")

    def test_dragon_docstring_contains_description(self):
        self.assertIn("chaotic evil", self.classes["TestAncientDragon"].__doc__)

    def test_empty_optional_fields_default_to_empty_string(self):
        goblin = self.classes["TestGoblin"]
        self.assertEqual(goblin.damage_immunities, "")
        self.assertEqual(goblin.damage_resistances, "")
        self.assertEqual(goblin.damage_vulnerabilities, "")
        self.assertEqual(goblin.condition_immunities, "")
        self.assertEqual(goblin.saving_throws, "")


class TestLoadYamlMonsterClassesListFields(TestCase):
    """Verify list field (traits, actions, legendary_actions, reactions) handling."""

    @classmethod
    def setUpClass(cls):
        cls.classes = load_yaml_monster_classes(_MONSTERS_YAML, Monster)

    def test_goblin_has_empty_list_fields(self):
        goblin = self.classes["TestGoblin"]
        self.assertEqual(goblin.traits, [])
        self.assertEqual(goblin.actions, [])
        self.assertEqual(goblin.legendary_actions, [])
        self.assertEqual(goblin.reactions, [])

    def test_ogre_traits(self):
        ogre = self.classes["TestOgre"]
        self.assertEqual(len(ogre.traits), 1)
        self.assertEqual(ogre.traits[0]["name"], "Siege Monster")
        self.assertIn("double damage", ogre.traits[0]["description"])

    def test_ogre_actions(self):
        ogre = self.classes["TestOgre"]
        self.assertEqual(len(ogre.actions), 2)
        action_names = [a["name"] for a in ogre.actions]
        self.assertIn("Greatclub", action_names)
        self.assertIn("Javelin", action_names)

    def test_ogre_action_has_description(self):
        ogre = self.classes["TestOgre"]
        greatclub = next(a for a in ogre.actions if a["name"] == "Greatclub")
        self.assertIn("bludgeoning", greatclub["description"])

    def test_dragon_traits(self):
        dragon = self.classes["TestAncientDragon"]
        self.assertEqual(len(dragon.traits), 2)
        trait_names = [t["name"] for t in dragon.traits]
        self.assertIn("Legendary Resistance (3/Day)", trait_names)

    def test_dragon_legendary_actions(self):
        dragon = self.classes["TestAncientDragon"]
        self.assertEqual(len(dragon.legendary_actions), 3)
        la_names = [la["name"] for la in dragon.legendary_actions]
        self.assertIn("Detect", la_names)
        self.assertIn("Wing Attack (Costs 2 Actions)", la_names)

    def test_dragon_reactions(self):
        dragon = self.classes["TestAncientDragon"]
        self.assertEqual(len(dragon.reactions), 1)
        self.assertEqual(dragon.reactions[0]["name"], "Tail Lash")

    def test_list_fields_are_lists_of_dicts(self):
        dragon = self.classes["TestAncientDragon"]
        for field in ("traits", "actions", "legendary_actions", "reactions"):
            with self.subTest(field=field):
                field_val = getattr(dragon, field)
                self.assertIsInstance(field_val, list)
                for item in field_val:
                    self.assertIsInstance(item, dict)
                    self.assertIn("name", item)
                    self.assertIn("description", item)


class TestLoadYamlMonsterClassesRegistry(TestCase):
    """Verify that generated monster classes can be registered and resolved."""

    def _make_registry_with_classes(self, generated):
        """Create a fresh ContentRegistry populated with *generated* classes."""
        mod_name = "_test_yaml_monsters_tmp"
        mod = types.ModuleType(mod_name)
        for name, cls in generated.items():
            setattr(mod, name, cls)
        sys.modules[mod_name] = mod
        registry = ContentRegistry()
        registry.add_module(mod_name)
        return registry, mod_name

    def tearDown(self):
        sys.modules.pop("_test_yaml_monsters_tmp", None)

    def test_classes_resolvable_by_class_name(self):
        generated = load_yaml_monster_classes(_MONSTERS_YAML, Monster)
        registry, _ = self._make_registry_with_classes(generated)
        found = registry.findattr("TestGoblin", valid_classes=[Monster])
        self.assertIs(found, generated["TestGoblin"])

    def test_classes_resolvable_by_display_name(self):
        # Registry looks up by module attribute name; generate a class whose
        # class_name matches the display name so we can verify lookup by name.
        with TemporaryDirectory() as tmp_dir:
            yaml_dir = Path(tmp_dir)
            yaml_dir.joinpath("monsters.yaml").write_text(
                "- class_name: Goblin\n  name: Goblin\n  challenge_rating: 0.25\n",
                encoding="utf-8",
            )
            generated = load_yaml_monster_classes(yaml_dir, Monster)
        registry, _ = self._make_registry_with_classes(generated)
        found = registry.findattr("Goblin", valid_classes=[Monster])
        self.assertIs(found, generated["Goblin"])

    def test_module_attribute_is_set(self):
        generated = load_yaml_monster_classes(
            _MONSTERS_YAML, Monster, module="dungeonsheets.monsters"
        )
        self.assertEqual(generated["TestGoblin"].__module__, "dungeonsheets.monsters")

    def test_default_module_is_yaml_content(self):
        generated = load_yaml_monster_classes(_MONSTERS_YAML, Monster)
        self.assertEqual(generated["TestGoblin"].__module__, "dungeonsheets.yaml_content")


class TestLoadYamlMonsterClassesDirectory(TestCase):
    """Verify that the loader handles a directory of YAML files."""

    def test_loads_from_directory_with_multiple_files(self):
        with TemporaryDirectory() as tmp_dir:
            yaml_dir = Path(tmp_dir)
            yaml_dir.joinpath("monsters_a.yaml").write_text(
                "- class_name: AshGhoul\n  name: Ash Ghoul\n  challenge_rating: 1\n",
                encoding="utf-8",
            )
            yaml_dir.joinpath("monsters_b.yaml").write_text(
                "- class_name: BloodBear\n  name: Blood Bear\n  challenge_rating: 3\n",
                encoding="utf-8",
            )

            generated = load_yaml_monster_classes(yaml_dir, Monster)

            self.assertIn("AshGhoul", generated)
            self.assertIn("BloodBear", generated)

    def test_directory_loader_sets_data_source(self):
        with TemporaryDirectory() as tmp_dir:
            yaml_dir = Path(tmp_dir)
            yaml_dir.joinpath("monsters_a.yaml").write_text(
                "- class_name: AshGhoul\n  name: Ash Ghoul\n",
                encoding="utf-8",
            )

            generated = load_yaml_monster_classes(yaml_dir, Monster)

            self.assertEqual(generated["AshGhoul"].data_source, "yaml")

    def test_raises_on_duplicate_class_names_across_files(self):
        with TemporaryDirectory() as tmp_dir:
            yaml_dir = Path(tmp_dir)
            yaml_dir.joinpath("monsters_a.yaml").write_text(
                "- class_name: DuplicateMonster\n  name: Duplicate One\n",
                encoding="utf-8",
            )
            yaml_dir.joinpath("monsters_b.yaml").write_text(
                "- class_name: DuplicateMonster\n  name: Duplicate Two\n",
                encoding="utf-8",
            )

            with self.assertRaises(ValueError) as ctx:
                load_yaml_monster_classes(yaml_dir, Monster)

            self.assertIn("DuplicateMonster", str(ctx.exception))

    def test_raises_on_string_list_field(self):
        with TemporaryDirectory() as tmp_dir:
            yaml_dir = Path(tmp_dir)
            yaml_dir.joinpath("monsters_a.yaml").write_text(
                "- class_name: BadMonster\n  name: Bad Monster\n  traits: not-a-list\n",
                encoding="utf-8",
            )

            with self.assertRaises(ValueError) as ctx:
                load_yaml_monster_classes(yaml_dir, Monster)

            self.assertIn("traits", str(ctx.exception))

    def test_single_file_path_works(self):
        generated = load_yaml_monster_classes(_MONSTERS_YAML, Monster)
        self.assertEqual(len(generated), 3)
