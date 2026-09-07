# Asset Development Prompt Log

Tracks execution of `docs/architecture/asset-roadmap.md`. Each row is a
standalone prompt file, written to be pasted into a **fresh** Claude Code
session (no memory of any other session, including the one that wrote the
prompt) — so every prompt file is self-contained: it points at the roadmap
doc and CLAUDE.md rather than assuming shared context.

**Workflow:** prompt is written here → user runs it in a new session → user
reports back → prompt's author reviews the result against its acceptance
criteria → either changes are requested (same prompt file gets a "Round 2"
addendum) or it's marked Approved and the next prompt is written.

**Why these files are kept (not gitignored):** they're the intent-and-spec
record the roadmap's own Decisions Log convention already models — a prompt
captures *why* an asset batch was scoped the way it was, which the resulting
code alone can't tell a future reader. Addenda go in the same file, appended,
never rewriting history in place (same rule the roadmap holds itself to).

Only Phase 0's prompt is written in full right now. Later phases are outlined
below and get fully drafted just-in-time — several (Phase 2 onward) depend on
Phase 1's customData-vs-manifest finding, which doesn't exist yet.

## Branching & merging

One branch **per roadmap phase**, not per individual prompt file — the
3a/3b and 4a/4b prompt splits below exist to keep the review loop tight, not
because they're independently mergeable (a half-built shared kit with no
assets assembled on it yet isn't worth shipping alone). The roadmap already
declares each *phase* the atomic, independently-testable unit.

- **Branch:** `feat/phase<N>-<slug>`, created off an up-to-date `main`
  before that phase's first prompt runs.
- **Commit:** one commit per prompt, added only after that prompt's result
  is reviewed and approved (a rejected round stays uncommitted, so there's
  nothing to unwind) — so a two-prompt phase (3, 4) shows up as two commits
  on one branch.
- **PR:** opened once every prompt belonging to the phase is approved,
  merged into `main`, branch deleted. The next phase branches off the
  freshly updated `main`.
- Each prompt file's "before you start" step names the branch to check out
  (create it for a phase's first prompt, reuse it for the second) — a fresh
  session has no memory of this plan otherwise.

## Prompt sequence

| # | File | Roadmap phase | Branch | Scope | Status |
|---|---|---|---|---|---|
| 1 | [phase0-core-utils.md](phase0-core-utils.md) | Phase 0 | `feat/phase0-core-utils` | Rig/hardpoint/UV/material-preset/manifest helpers + `create_asset_stage()` scope builder | **Approved — PR open** |
| 2 | phase1-pipeline-validation.md | Phase 1 | `feat/phase1-pipeline-validation` | Spike test asset; full usdz+glb export round-trip; resolve customData-vs-manifest question; Babylon suffix-lookup smoke test | Not written — depends on 1 |
| 3 | phase2-cargo-props-characters.md | Phase 2 | `feat/phase2-cargo-props-characters` | Cargo container kit (5 variants), prop kit, stacked-pallet bake test, 6 placeholder Character proxies | Not written — depends on 2's metadata decision |
| 4 | phase3a-vehicle-kit-and-mule.md | Phase 3 (part A, addendum) | `feat/phase3-vehicle-roster` | Shared vehicle kit (chassis/wheel/suspension/hinge/latch/lighting) built and proven on one reference vehicle (the Mule), incl. Babylon steer/spin validation | Not written |
| 5 | phase3b-remaining-vehicles.md | Phase 3 (part B, addendum) | `feat/phase3-vehicle-roster` (same branch as 4) | Goat, Needle, Bastion, Wasp assembled from the kit 3a validated | Not written |
| 6 | phase4a-terrain-tiles-hazards.md | Phase 4 (part A, addendum) | `feat/phase4-terrain` | Road tile kit + tile-snap convention + 4 named hazard tiles + chained test route | Not written |
| 7 | phase4b-biome-dressing-variants.md | Phase 4 (part B, addendum) | `feat/phase4-terrain` (same branch as 6) | Biome dressing kits (neutral/mountain/swamp/dockside) + calmed/militarized `UsdVariantSets` + per-tile gameplay tags | Not written |
| 8 | phase5-advanced-hazards-integration.md | Phase 5 | `feat/phase5-advanced-hazards` | Checkpoint, pursuit/escort chassis-reuse liveries, ambush/hot-zone props, tier-5 composite integration test | Not written |

Phase 6 (character rigging / on-foot mechanics) stays deferred per the
roadmap — no prompt until a design pass greenlights it.

The 3a/3b and 4a/4b splits are this log's addendum to the roadmap, not
something `asset-roadmap.md` itself specifies — each pairs a "build the
reusable kit" step (needs the most scrutiny, unlocks everything after it)
with a "stamp out N assets from the proven kit" step (mostly repetition).
If a phase turns out to fit in one session anyway, that's fine — merge back
down when writing the prompt.

## Review Log

_(Append one dated entry per reviewed prompt: what shipped, what was
accepted as-is, what needed a Round 2, and any decision that changes later
prompts — e.g. Phase 1's metadata-channel outcome belongs here.)_

- **2026-09-06 — Phase 0 (`phase0-core-utils.md`): Approved, no changes
  requested.** Independently re-verified rather than trusting the executing
  session's self-report: built the exact test asset the prompt specifies
  (chassis box, `_Spin`-pivoted wheel, `TieDown_01` hardpoint) using only
  the new helpers, flattened it, and confirmed `usdchecker` reports
  `Success` and `usdtree` matches the §2.1/§2.2/§2.3 skeleton exactly, with
  `Wheel_FL_Spin` the parent of `Wheel_FL_Mesh` (not a sibling). Suffix,
  category, and material-preset validation all raise on bad input as
  required. `get_material`/`set_color`'s new `preset=None` default doesn't
  break `build_assets.py`'s existing 2-arg call site. The throwaway test
  script was deleted rather than committed, per the prompt's ask. Shipped
  on `feat/phase0-core-utils`.
