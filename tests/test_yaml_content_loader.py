from importlib.resources import files
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from dungeonsheets.magic_items import MagicItem
from dungeonsheets.spells.spells import Spell
from dungeonsheets.yaml_content import (
    _resolve_yaml_sources,
    load_yaml_magic_item_classes,
    load_yaml_spell_classes,
)


class TestSplitYamlLoader(TestCase):
    def test_spell_loader_supports_directory_sources(self):
        with TemporaryDirectory() as tmp_dir:
            yaml_dir = Path(tmp_dir)
            yaml_dir.joinpath("spells_a.yaml").write_text(
                """
- class_name: ArcaneWhisper
  name: Arcane Whisper
  level: 1
  classes:
    - Wizard
""".lstrip(),
                encoding="utf-8",
            )
            yaml_dir.joinpath("spells_b.yaml").write_text(
                """
- class_name: BattleHymn
  name: Battle Hymn
  level: 2
  classes:
    - Bard
""".lstrip(),
                encoding="utf-8",
            )

            generated = load_yaml_spell_classes(yaml_dir, Spell)

            self.assertIn("ArcaneWhisper", generated)
            self.assertIn("BattleHymn", generated)
            self.assertEqual(generated["ArcaneWhisper"].data_source, "yaml")
            self.assertEqual(generated["BattleHymn"].classes, ("Bard",))

    def test_magic_item_loader_supports_directory_sources(self):
        with TemporaryDirectory() as tmp_dir:
            yaml_dir = Path(tmp_dir)
            yaml_dir.joinpath("magic_items_a.yaml").write_text(
                """
- class_name: AmberRing
  name: Amber Ring
  rarity: Rare
  item_type: Ring
""".lstrip(),
                encoding="utf-8",
            )
            yaml_dir.joinpath("magic_items_b.yaml").write_text(
                """
- class_name: BronzeAmulet
  name: Bronze Amulet
  rarity: Uncommon
  item_type: Wondrous Item
""".lstrip(),
                encoding="utf-8",
            )

            generated = load_yaml_magic_item_classes(yaml_dir, MagicItem)

            self.assertIn("AmberRing", generated)
            self.assertIn("BronzeAmulet", generated)
            self.assertEqual(generated["AmberRing"].data_source, "yaml")
            self.assertEqual(generated["BronzeAmulet"].item_type, "Wondrous Item")

    def test_spell_loader_raises_on_duplicate_class_names_across_files(self):
        with TemporaryDirectory() as tmp_dir:
            yaml_dir = Path(tmp_dir)
            yaml_dir.joinpath("spells_a.yaml").write_text(
                """
- class_name: DuplicateSpell
  name: Duplicate Spell
""".lstrip(),
                encoding="utf-8",
            )
            yaml_dir.joinpath("spells_b.yaml").write_text(
                """
- class_name: DuplicateSpell
  name: Duplicate Spell Two
""".lstrip(),
                encoding="utf-8",
            )

            with self.assertRaises(ValueError):
                load_yaml_spell_classes(yaml_dir, Spell)

    def test_spell_loader_sets_module_on_generated_classes(self):
        with TemporaryDirectory() as tmp_dir:
            yaml_dir = Path(tmp_dir)
            yaml_dir.joinpath("spells_a.yaml").write_text(
                """
- class_name: ArcaneWhisper
  name: Arcane Whisper
  level: 1
  classes:
    - Wizard
""".lstrip(),
                encoding="utf-8",
            )

            generated = load_yaml_spell_classes(yaml_dir, Spell, module="dungeonsheets.spells")

            self.assertEqual(generated["ArcaneWhisper"].__module__, "dungeonsheets.spells")

    def test_spell_loader_default_module_is_yaml_content(self):
        with TemporaryDirectory() as tmp_dir:
            yaml_dir = Path(tmp_dir)
            yaml_dir.joinpath("spells_a.yaml").write_text(
                """
- class_name: ArcaneWhisper
  name: Arcane Whisper
  level: 1
""".lstrip(),
                encoding="utf-8",
            )

            generated = load_yaml_spell_classes(yaml_dir, Spell)

            # When module is not passed, __module__ is set by type() to the
            # frame where the class is created — yaml_content.
            self.assertEqual(generated["ArcaneWhisper"].__module__, "dungeonsheets.yaml_content")

    def test_spell_loader_raises_on_string_classes_field(self):
        with TemporaryDirectory() as tmp_dir:
            yaml_dir = Path(tmp_dir)
            yaml_dir.joinpath("spells_a.yaml").write_text(
                """
- class_name: BadSpell
  name: Bad Spell
  classes: Wizard
""".lstrip(),
                encoding="utf-8",
            )

            with self.assertRaises(ValueError) as ctx:
                load_yaml_spell_classes(yaml_dir, Spell)

            self.assertIn("classes", str(ctx.exception))

    def test_spell_loader_raises_on_string_components_field(self):
        with TemporaryDirectory() as tmp_dir:
            yaml_dir = Path(tmp_dir)
            yaml_dir.joinpath("spells_a.yaml").write_text(
                """
- class_name: BadSpell
  name: Bad Spell
  components: V
""".lstrip(),
                encoding="utf-8",
            )

            with self.assertRaises(ValueError) as ctx:
                load_yaml_spell_classes(yaml_dir, Spell)

            self.assertIn("components", str(ctx.exception))

    def test_magic_item_loader_raises_on_string_linked_spells_field(self):
        with TemporaryDirectory() as tmp_dir:
            yaml_dir = Path(tmp_dir)
            yaml_dir.joinpath("items_a.yaml").write_text(
                """
- class_name: BadWand
  name: Bad Wand
  linked_spells: Fireball
""".lstrip(),
                encoding="utf-8",
            )

            with self.assertRaises(ValueError) as ctx:
                load_yaml_magic_item_classes(yaml_dir, MagicItem)

            self.assertIn("linked_spells", str(ctx.exception))

    def test_resolve_yaml_sources_supports_traversable_directory(self):
        spells_dir = files("dungeonsheets.data").joinpath("spells")
        sources = _resolve_yaml_sources(spells_dir)

        self.assertGreater(len(sources), 0)
        self.assertTrue(all(source.name.endswith(".yaml") for source in sources))

    def test_spell_loader_supports_traversable_directory(self):
        spells_dir = files("dungeonsheets.data").joinpath("spells")
        generated = load_yaml_spell_classes(spells_dir, Spell)

        self.assertIn("MagicMissile", generated)
        self.assertEqual(generated["MagicMissile"].data_source, "yaml")
