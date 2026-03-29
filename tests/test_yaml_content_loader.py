from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from dungeonsheets.magic_items import MagicItem
from dungeonsheets.spells.spells import Spell
from dungeonsheets.yaml_content import load_yaml_magic_item_classes, load_yaml_spell_classes


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
