Architecture Decision 0001: Renderer Strategy for LaTeX/PDF Pipeline
=====================================================================

Status
------
Accepted (Phase 1 spike for issue #27)

Date
----
2026-04-14

Context
-------
The current output pipeline combines several rendering paths:

- Fillable PDF sheets are produced from templates via ``fill_pdf_template.py``
  using ``pdftk`` with a ``pypdf`` fallback.
- Extra pages (features, magic items, some spell/notes content) are rendered
  through LaTeX in ``latex.py`` and then merged.
- ePub output already uses a pure-Python HTML path in ``epub.py``.

This architecture works functionally but has high operational risk:

- CI and container builds require a large TeX Live toolchain.
- LaTeX engine/package behavior can regress outside our code changes.
- Contributor setup is harder due to external binary dependencies.

During Phase 0 validation, Docker tests showed a current lualatex/luaotfload
regression unrelated to app code. That validates issue #27's core concern:
external TeX runtime volatility can block delivery.

Decision
--------
Choose **Track B: Hybrid renderer abstraction with phased migration**.

We will keep LaTeX support for compatibility while introducing a renderer
abstraction layer and incrementally moving LaTeX-generated content to a
non-LaTeX backend where practical.

Why this track
--------------

- Track A (keep LaTeX core) does not materially reduce dependency risk.
- Track C (full replacement now) is too disruptive given current templates,
  output expectations, and ongoing roadmap items.
- Track B gives immediate risk reduction while preserving user-facing behavior
  and allowing incremental, testable migration slices.

Options considered
------------------

Track A: Keep LaTeX core and reduce pain points
  Pros: Lowest short-term code churn.
  Cons: Keeps TeX dependency as a critical path and does not solve long-term
  reliability concerns.

Track B: Hybrid abstraction and phased migration (**selected**)
  Pros: Enables controlled migration, reduces CI/runtime fragility over time,
  keeps backward compatibility during transition.
  Cons: Temporary dual-path complexity until migration completes.

Track C: Full migration away from LaTeX now
  Pros: Single backend target and largest long-term simplification.
  Cons: High near-term rewrite risk and potential output parity regressions.

Scope
-----

Phase 1 scope (this decision):

- Record the architectural direction and constraints.
- Define migration sequence and acceptance criteria.
- Leave user-visible behavior unchanged in this step.

Out of scope for Phase 1:

- Replacing all LaTeX templates immediately.
- Removing ``lualatex`` or ``pdftk`` dependencies in one change.
- Large template/style redesign.

Constraints
-----------

- Preserve output parity for core artifacts:

  - Character sheet PDF
  - Extra content pages (features, magic items, notes)
  - Spell sheet behavior
  - ePub output

- Keep current CLI behavior and flags stable.
- Keep fallback behavior intact where external binaries are unavailable.
- Land changes in small slices with targeted regression tests.

Implementation plan (phased)
----------------------------

1. Introduce renderer abstraction

   - Define internal renderer interface for extra pages and spell pages.
   - Route ``make_sheets.py`` through the interface without changing defaults.

2. Migrate one low-risk content surface first

   - Start with one non-critical extra-page output path and verify parity.
   - Keep LaTeX as fallback/feature flag during migration.

3. Expand migration by domain

   - Migrate additional extra pages and spell rendering in slices.
   - Keep each slice independently releasable.

4. Reassess deprecation timing

   - After parity and stability targets are met, decide whether to deprecate
     mandatory LaTeX runtime requirements.

Acceptance criteria
-------------------

- Existing tests for ``make_sheets``, ``latex``, and relevant integration paths
  remain green.
- Representative sample outputs are generated successfully for both PDF and ePub
  during migration steps.
- Each migrated slice preserves content correctness and ordering.
- CI no longer treats LaTeX as a single point of failure for all rendering
  workflows once hybrid fallback is in place.

Consequences
------------

Positive:

- Reduces delivery risk from TeX ecosystem volatility.
- Allows migration without a high-risk big-bang rewrite.
- Improves contributor and CI ergonomics over time.

Negative:

- Requires temporary maintenance of dual rendering paths.
- Needs disciplined regression checks to avoid parity drift.

References
----------

- Issue #27: consider migrating away from LaTeX dependency
- ``dungeonsheets/make_sheets.py``
- ``dungeonsheets/latex.py``
- ``dungeonsheets/fill_pdf_template.py``
- ``dungeonsheets/epub.py``
