## Plan: Decouple Magic Item Form From Effects

Refactor magic items from inheritance-based “item classes with embedded bonuses” into a composition model: each item has a `form` (what it is) and `effects` (what it does). This directly supports scrolls/potions as spell carriers and lets magical weapon properties apply to any weapon type.

**Steps**
1. Phase 1: Introduce a composable effect model.
2. Add effect types for `SavingThrowBonus`, `ArmorClassBonus`, `WeaponModifier`, `SpellGranted`, `PassiveTrait`, and `ChargePool` (data only).
3. Add a `MagicItemForm` model (`kind`, `base_item`, `rarity`, `requires_attunement`, consumable flags).
4. Update `MagicItem` to hold `form + effects` instead of hard-coded stat attributes.
5. Phase 2: Rewire stat aggregation.
6. Update AC/ST calculations to aggregate from effects rather than reading `ac_bonus` / `st_bonus_*` directly.
7. Keep a short-lived compatibility shim for legacy item attributes during migration, then remove it (breaking changes are acceptable).
8. Update character item loading so legacy definitions can be normalized into the new shape while refactoring.
9. Phase 3: Make magical weapon effects reusable across weapon forms.
10. Add deterministic application of `WeaponModifierEffect` to any weapon instance using filters (weapon class and/or property tags).
11. Integrate with existing weapon lifecycle so ordering is explicit (recommended: after base init, before feature hooks).
12. Add helper factories like “plus-N weapon property” so effects are reusable without multiple inheritance.
13. Phase 4: Add consumable spell effects.
14. Represent scrolls/potions as consumable forms with one or more `SpellGrantedEffect`s.
15. Resolve spells through existing content registry for validation/normalization.
16. Expose spell effects and charge metadata in output text/sheets; do not implement runtime consumption tracking yet.
17. Phase 5: Migrate representative items and expand tests.
18. Convert a defensive item, a magical weapon, and a charged caster item to the new model.
19. Add explicit potion/scroll examples.
20. Update tests for AC/ST aggregation, reusable weapon properties across multiple weapon classes, spell-granting consumables, and charge metadata.

**Relevant files**
- `/home/james/source/github/stiffneckjim/dungeon-sheets/dungeonsheets/magic_items.py` - core model refactor and item conversions.
- `/home/james/source/github/stiffneckjim/dungeon-sheets/dungeonsheets/stats.py` - AC/ST aggregation from effects.
- `/home/james/source/github/github/stiffneckjim/dungeon-sheets/dungeonsheets/character.py` - item loading/normalization path.
- `/home/james/source/github/stiffneckjim/dungeon-sheets/dungeonsheets/weapons.py` - weapon effect application and ordering.
- `/home/james/source/github/stiffneckjim/dungeon-sheets/dungeonsheets/content_registry.py` - spell/item lookup normalization.
- `/home/james/source/github/stiffneckjim/dungeon-sheets/tests/test_magic_items.py` - effect composition tests.
- `/home/james/source/github/stiffneckjim/dungeon-sheets/tests/test_stats.py` - AC/ST regression tests.
- `/home/james/source/github/stiffneckjim/dungeon-sheets/tests/test_character.py` - loading/integration behavior.
- `/home/james/source/github/stiffneckjim/dungeon-sheets/tests/test_weapon.py` - cross-weapon reusable magic effects.

**Verification**
1. Run focused tests: `tests/test_magic_items.py`, `tests/test_weapon.py`, `tests/test_stats.py`, `tests/test_character.py`.
2. Run integration regressions: `tests/test_spells.py`, `tests/test_content_registry.py`, `tests/test_make_sheets.py`.
3. Manual smoke case with one potion + one scroll + one reusable weapon property attached to two different weapon classes.
4. Confirm exported item text includes spell effects and charge metadata.

**Decisions Captured**
- Breaking changes allowed.
- Included scope: weapon attack/damage bonuses, AC/ST bonuses, spell-granting effects, charge metadata, passive traits.
- Excluded scope: runtime use/charge consumption state.
- Recommended direction: composition over multi-inheritance.

If you approve, this plan is ready for handoff to implementation.