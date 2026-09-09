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

Phases 0–2 are drafted; Phase 3 onward get fully drafted just-in-time, since
their prompts should reflect whatever conventions the immediately-preceding
phase actually landed on (see each phase's Review Log entry for those).

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
| 1 | [phase0-core-utils.md](phase0-core-utils.md) | Phase 0 | `feat/phase0-core-utils` | Rig/hardpoint/UV/material-preset/manifest helpers + `create_asset_stage()` scope builder | **Approved — merged (PR #3)** |
| 2 | [phase1-pipeline-validation.md](phase1-pipeline-validation.md) | Phase 1 | `feat/phase1-pipeline-validation` | Spike test asset; full usdz+glb export round-trip; resolve customData-vs-manifest question; Babylon suffix-lookup smoke test | **Approved — merged (PR #4)** |
| 3 | [phase2-cargo-props-characters.md](phase2-cargo-props-characters.md) | Phase 2 | `feat/phase2-cargo-props-characters` | Cargo container kit (5 variants), prop kit, stacked-pallet bake test, 6 placeholder Character proxies | **Approved — merged (PR #5)** |
| 4 | ~~[phase3a-vehicle-kit-and-mule.md](phase3a-vehicle-kit-and-mule.md)~~ | Phase 3 | `feat/phase3-vehicle-roster` | **Superseded, not run to completion as-is** — box-only kit read as "a poorly designed toy" on review; replaced by the profile-extrusion + referenced-parts plan below (rows 4a-4c) | Superseded |
| 4a | [phase3a-shared-vehicle-kit.md](phase3a-shared-vehicle-kit.md) | Phase 3 (part A, revised) | `feat/phase3-vehicle-roster` | Shared/customizable kit: profile-extrusion + frustum geometry helpers, a referenceable wheel-corner sub-asset generator, detail/greeble kit | **Approved** |
| 4b | [phase3b-mule.md](phase3b-mule.md) | Phase 3 (part B, revised) | `feat/phase3-vehicle-roster` (same branch) | The Mule assembled from 4a's kit: profile-extruded hood/windshield, referenced wheel corners, cargo box, details, hardpoints, collision, door-hinge/cargo-latch kit additions | **Approved** (after two Round 2 fixes) |
| 4c | [phase3c-goat-reuse-proof.md](phase3c-goat-reuse-proof.md) | Phase 3 (part C, revised) | `feat/phase3-vehicle-roster` (same branch) | The Goat assembled from the *same* kit with different parameters (pickup proportions, open bed, off-road tires, long-travel suspension), plus a suspension-strut mounting fix (affects the Mule too) and a generalized hinge-axis for the tailgate — the explicit proof that 4a's kit is genuinely reusable, not Mule-specific | **Approved** |
| 4d+ | TBD | Phase 3 (remainder) | TBD | Needle, Bastion (likely mostly kit reuse per 4c's proof) and the Wasp (motorcycle — expected to need its own bespoke pipeline, not this kit) | Not written — planned after 4c's proof lands |
| 5 | phase4a-terrain-tiles-hazards.md | Phase 4 (part A, addendum) | `feat/phase4-terrain` | Road tile kit + tile-snap convention + 4 named hazard tiles + chained test route | Not written |
| 6 | phase4b-biome-dressing-variants.md | Phase 4 (part B, addendum) | `feat/phase4-terrain` (same branch as 5) | Biome dressing kits (neutral/mountain/swamp/dockside) + calmed/militarized `UsdVariantSets` + per-tile gameplay tags | Not written |
| 7 | phase5-advanced-hazards-integration.md | Phase 5 | `feat/phase5-advanced-hazards` | Checkpoint, pursuit/escort chassis-reuse liveries, ambush/hot-zone props, tier-5 composite integration test | Not written |

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

- **2026-09-06 — Phase 1 (`phase1-pipeline-validation.md`): Approved, no
  changes requested.** Independently reproduced both findings rather than
  trusting the self-report: rebuilt the test asset (zero-offset
  `_Steer`→`_Spin` wheel chain, `_Hinge` door, `TieDown_01` with
  `customData`), exported through the actual pipeline, and parsed the
  `.glb`'s JSON chunk directly — node names survive verbatim, `extras` is
  `null` on every node including `TieDown_01`, confirming customData does
  not survive. **Decision: the sidecar manifest
  (`manifest_utils.write_manifest`) is the required metadata path for
  Phase 2+**, now recorded in `asset-roadmap.md`'s Decisions Log.
  Additionally re-verified the session's own flagged deviation: a genuine
  bug in `pipeline/blender_usd_to_gltf.py` where Blender's USD importer
  default (`merge_parent_xform=True`) silently drops any zero-offset
  Xform-with-one-child — exactly the shape of a `_Spin` pivot nested
  directly under `_Steer`, or any hinge at its own local origin. Reproduced
  the pre-fix behavior myself: both `Wheel_FL_Spin` and `Door_Hinge`
  vanished from the exported glTF, their child mesh reparented directly to
  the grandparent. The applied fix (`merge_parent_xform=False`) resolves it
  confirmed. This is a shared-pipeline correctness fix, not scope creep —
  every phase from here on depends on pivots surviving export, so good call
  flagging and fixing it now rather than deferring. `main.ts`'s temporary
  test snippet and the throwaway `pipeline/phase1_test_asset.py` were both
  cleanly removed. Shipped on `feat/phase1-pipeline-validation`.

- **2026-09-07 — Phase 2 (`phase2-cargo-props-characters.md`): Approved,
  one comment corrected, no functional changes requested.** Independently
  reran `pipeline/build_cargo.py` and confirmed all 5 containers export
  clean (`usdchecker` `Success` on every `.usdz`) with visually distinct
  materials (wood: plain color, glass: `glass-preview`, steel/machine-parts/
  drum: `steel`, sealed: `unmarked-matte`). Reproduced and independently
  verified two real shared-pipeline bugs the session found and fixed beyond
  this prompt's literal scope, both good calls to fix now rather than defer:
  - `get_material`'s cache was keyed by `id(stage)`; a build script that
    creates and discards one `Usd.Stage` per asset (every script from this
    phase on) hits CPython reusing a freed stage's `id()` for the next one.
    Confirmed reproducible directly (`id()` collided on every iteration of
    a tight create/discard loop). Fixed by keying on
    `stage.GetRootLayer().identifier` instead; independently confirmed
    every container's `MaterialBindingAPI` relationship target resolves to
    a real prim under its own default prim post-fix. Corrected one inline
    comment that cited `usdchecker`'s `MaterialBindingCollectionValidator`
    as having caught this — that validator is about `UsdCollectionAPI`-based
    bindings, unrelated; it wouldn't have flagged a dangling direct-binding
    relationship. The bug and fix themselves were correct, just that one
    citation wasn't — corrected in place rather than bouncing back for a
    documentation-only fix.
  - `bake_point_instancer` never deactivated the baked template copy or the
    external-reference prototype prim itself, only the instancer — leaving
    live, untransformed duplicates at the origin. Reproduced the stacking
    test independently (4 crates referencing an exported cargo container as
    an external-reference `PointInstancer` prototype): confirmed the
    flattened, exported output contains only the 4 baked instances and
    nothing else — no leftover prototype, template, or instancer prim
    survives flatten once deactivated.
  Anchor-alignment reasoning double-checked by inspection rather than
  re-running a script: `Anchor` sits at local origin `(0,0,0)` on every
  character, so aligning to a `DriverSeat` is pure translation of the
  character's own root — no per-character offset math needed, confirming
  the contract holds trivially. All 6 character placeholders (capsule via
  `make_cylinder_mesh`, no dedicated capsule-mesh helper needed) export
  clean with a distinct color and an `Anchor` hardpoint each. `npm run
  check` passes. Both throwaway validation scripts (stacking test,
  anchor-alignment test) were removed, not committed. Shipped on
  `feat/phase2-cargo-props-characters`.

- **2026-09-07 — Phase 3a (`phase3a-vehicle-kit-and-mule.md`): rejected,
  redesigned rather than patched.** The executing session's Mule was built
  entirely from axis-aligned boxes/cylinders (chassis as one full-length
  flat slab, cargo box as a plain shoebox, wheels as bare 16-sided
  cylinders) — reviewed by rendering it headlessly via Blender (not just
  reading the code) and independently confirmed it read as "a poorly
  designed toy," matching the user's own reaction from viewing it directly.
  Rather than iterate on that draft, prototyped three revisions directly
  (v2/v3/v4, outside the phase-prompt workflow, purely to validate a
  direction before committing a new prompt to it) using only the *existing*
  primitive helpers composed with real vehicle anatomy — hood, cab,
  windshield/side glass, wheel-arch flares, bumpers, two-tone rocker,
  rim+tire wheel split — landing on v4 as "pleasant, stylized low-poly,"
  after v3 introduced and then fixed a real regression (oversized side-glass
  panels reading as solid wall panels). The user then pointed at a separate
  reference project, `modular-tank-learning-project` (a prior session's
  OpenUSD tank build), as the target quality/architecture bar. Reading its
  six generator scripts end-to-end (and rendering its output, not just
  reading code) surfaced two techniques our vehicle kit was missing:
  **profile-extrusion** for sloped panels (the tank's hull is a 5-point
  polygon extruded across width, not a box — this is what a real glacis
  plate needs, and what our Mule's hood/roofline should use instead of flat
  boxes) and a **real USD-referenced compositional pipeline** (leaf parts
  as their own `.usda` files, referenced with transform/variant overrides
  into an assembly, rigging and motion kept as separate layers on top) in
  place of one flat inline-authored stage per asset. One point the other
  direction: that project's own `PointInstancer`-baking export script
  doesn't deactivate its copied template prim — the same leftover-geometry
  bug this project's Phase 2 review already caught and fixed in our own
  `export_utils.py` — so our export-safety plumbing isn't behind.
  **Decision:** redo Phase 3 as three prompts instead of two —
  `phase3a-shared-vehicle-kit.md` (profile-extrusion/frustum helpers, a
  referenceable wheel-corner sub-asset, detail kit), `phase3b-mule.md` (the
  Mule assembled from that kit), `phase3c-goat-reuse-proof.md` (the Goat,
  same kit, different parameters — chosen over Bastion/Needle specifically
  to stress-test genericity, since it diverges further from the Mule's
  anatomy; the Wasp motorcycle is expected to need its own bespoke pipeline
  regardless and isn't a fair reuse test). Per the user's explicit
  trade-off: prioritize realism/detail over speed here. The old prompt file
  is kept, marked superseded, not deleted, per this log's own convention.

- **2026-09-07 — Phase 3a-revised (`phase3a-shared-vehicle-kit.md`):
  Approved, no changes requested.** Independently re-verified rather than
  trusting the report: rebuilt both a front (`steerable=True`) and rear
  wheel-corner asset directly, confirmed `usdchecker` clean on both and
  `usdtree` shows the exact expected pivot chains (`Wheel_Steer` ->
  `Wheel_Spin` for the front corner, bare `Wheel_Spin` for the rear — no
  `_Steer` parent). Rebuilt every Phase 2 asset (cargo/props/characters)
  after the `make_cylinder_mesh` refactor (now a thin wrapper over the new
  `make_frustum_mesh`) and ran `usdchecker` across every exported `.usdz` in
  `public/assets/models/` — all clean, confirming the refactor didn't
  regress existing callers. Looked at the session's own validation renders
  (`pipeline/.build/_review/phase3a_validate_a.png`/`_b.png`,
  `phase3a_detail_check*.png`) rather than trusting a text report: the
  curved wheel-arch flare (`make_profile_extrusion`, an annular-sector
  cross-section) reads convincingly on all four mirrored corners, the test
  frustum tapers correctly (not inside-out), the test profile-extruded
  wedge fills and shades correctly, and the window band from
  `build_window_band` is now a modest proportionate strip — the exact
  mistake (an oversized glass panel reading as a solid wall) from the
  earlier v3 prototype does not recur. `npm run check` passes. No leftover
  throwaway validation script (confirmed via search — only its `.usda`/`.png`
  outputs remain, gitignored). One stale `vehicle_Mule.usda`/`vehicle_mule.glb`
  found in `.build`/`public/assets/models` predates this session (leftover
  from the discarded first Phase 3a attempt) — noted, not a defect in this
  session's work, harmless since gitignored. Shipped on
  `feat/phase3-vehicle-roster` (first of three commits on this shared
  branch — Phase 3's branch/PR policy differs from earlier phases: one PR
  once 3a+3b+3c are all approved, not per prompt).

- **2026-09-07 — Phase 3b (`phase3b-mule.md`): Round 2 requested, not yet
  approved.** Independently verified rather than trusting the report.
  Confirmed a second real shared-pipeline bug, found and fixed by this
  session and re-verified by reproducing both sides myself: Blender's flat
  object namespace auto-deduplicates repeated pivot names (every wheel
  corner referenced twice authors identical leaf names like `Wheel_Spin`)
  by appending `.001`/`.002`/... *after* the name, silently breaking the
  `name.endsWith('_Spin')` suffix convention for every occurrence but the
  first. Reproduced pre-fix: only 1 of 4 `_Spin` and 1 of 2 `_Steer` nodes
  survived with a usable suffix. Confirmed the fix
  (`pipeline/blender_usd_to_gltf.py` now moves Blender's dedup tag to
  *before* the suffix) resolves it — all 4/2 nodes correct post-fix. Also
  confirmed: `usdchecker` clean, top-level scope skeleton correctly
  preserved despite nested wheel-corner references, `TieDown_01..04`
  numerically match `cargo_utils`' constants exactly, collision
  hulls/hardpoints/door-hinge/cargo-latch all present and correctly
  structured.
  **However**, looking at the session's own render images (multiple
  Blender angles *and* an actual in-engine Babylon screenshot) surfaced a
  real visual flaw the text-level checks didn't catch: a distracting
  ledge/shoulder where `CabGreenhouse` meets `CargoBox`. Confirmed via a
  direct world-space extent query that this is *not* the roofline-height
  mismatch it might look like (both tops sit at exactly `Y=2.35`, genuinely
  flush) but a **width** mismatch — the cargo box (`0.93` half-width) is
  wider than the greenhouse it meets (`0.78`) — contradicting the build
  script's own stated intent ("one continuous panel, no separate bridging
  trim") and reading worse at that seam than the discarded
  `mule_v4_prototype.png`. Requested a Round 2 fix (appended to
  `phase3b-mule.md`) rather than rejecting the whole phase — everything
  else here is solid. Left uncommitted per this log's own convention (a
  rejected round stays uncommitted, nothing to unwind).

  **Addendum, same day — a second Round 2 fix, found by the user viewing a
  wheel-corner asset directly in their own USD viewer:** the standalone
  `vehicle_mulefrontcorner.usda` (and the generic Phase 3a test corners,
  same code) is unrecognizable in isolation — "without the name, I'd have
  no idea what I'm looking at." Confirmed via direct `GetExtentAttr()`
  query, not just the visual complaint: the `Rim` mesh (local X span
  `[-0.077, 0.077]`, radius `0.22`) sits entirely *inside* the `Tire` mesh's
  solid volume (X span `[-0.11, 0.11]`, radius `0.36`) on every axis —
  completely hidden, contributing no visible geometry from any angle. The
  wheel-arch flare's default `arch_span_degrees=220` compounds it, wrapping
  most of the wheel's circumference rather than the top arch a real fender
  covers. Together: the one part meant to make this instantly readable as
  "a wheel" (the rim) is invisible, and the fender shell dominates the
  silhouette instead. Added as a second required fix to `phase3b-mule.md`'s
  Round 2 (rim offset to the tire's outboard face; arch span reduced to
  ~140-160°; re-verify by rendering a standalone wheel corner in isolation,
  the exact scenario that surfaced this) — same shared kit file every
  future vehicle calls, worth fixing before it propagates further.

- **2026-09-07 — Phase 3b (`phase3b-mule.md`): Round 2's two fixes applied
  and re-verified by rendering, not just re-reading the code.**

  **Cab/cargo-box seam:** `CabGreenhouse`'s half-width in
  `pipeline/build_vehicles.py` changed from `0.78` to
  `MULE_CARGO_BOX_HALF[0]` (`0.93`), matching the cargo box exactly instead
  of narrowing to it — the simpler of Round 2's two suggested options,
  taken because a flat match rendered clean (see below), so the more
  involved tapered-transition alternative wasn't needed. Rebuilt and
  rendered from several angles, including close 3/4 exterior shots aimed
  directly at the greenhouse/cargo-box top-side corner (the exact spot the
  original ledge was found); the corner now reads as one continuous flush
  panel with no poking-out step, confirmed against the pre-fix
  `mule_v5_final_a.png` side by side. `CabLower`'s own narrower width was
  left untouched per the prompt's own guidance, and didn't interact badly
  with the widened greenhouse.

  **Wheel-corner rim/arch:** in `pipeline/vehicle_utils.py`'s
  `build_wheel_corner`, `arch_span_degrees`'s default dropped from `220.0`
  to `150.0`. The rim fix deviates from the prompt's literal wording (an
  offset toward the tire's outboard face): since the SAME wheel-corner
  asset is referenced un-mirrored at both the +X and -X wheel positions
  (Task 4's own mirror-symmetric design), any offset toward one local-X
  side is only correct for one of the two referenced positions — at the
  other, that same local direction is the *inboard* face, occluded by the
  tire itself from the natural outward viewing angle, silently
  reintroducing the exact "wheel with no visible rim" bug on two of four
  wheels. Instead, added a new `rim_proud=0.02` parameter and sized the
  rim's own axial extent to `tire_width + 2 * rim_proud`, kept centered —
  the rim now protrudes symmetrically past both of the tire's flat faces,
  so it's visible regardless of which side ends up outboard when
  referenced. Re-verified by rendering `vehicle_mulefrontcorner.usda`
  alone from four angles (covering both local +X- and -X-facing views): the
  rim now shows clearly as a distinct lighter disc proud of the tire's
  face in every shot, and the fender arch reads as a partial cap over the
  wheel's top rather than a shell encasing it — both confirmed against the
  pre-fix `mule_v5_final_a.png`, where the wheel is a featureless black
  disc with an over-wide fender wrap.

  **Full-vehicle regression:** rebuilt the whole roster
  (`build_vehicles.py`), `usdchecker` clean on the Mule and both wheel-
  corner `.usdz` packages. Loaded `vehicle_mule.glb` in Babylon (temporary
  validation code in `main.ts`, removed before finishing, per this
  project's own throwaway-code convention): the multi-node suffix lookup
  (`name.endsWith('_Spin')` / `'_Steer'`) found all 4 `_Spin` and both
  `_Steer` nodes with correctly-deduped names (`Wheel_Spin`,
  `Wheel_001_Spin`, `Wheel_002_Spin`, `Wheel_003_Spin`; `Wheel_Steer`,
  `Wheel_001_Steer`) — confirming Round 2's first fix (the Blender
  namespace-dedup rename) still holds after this round's geometry changes.
  Sampled each pivot's rotation at two points in time and confirmed all six
  are actually turning, not just present. No console errors (aside from an
  expected headless-Chromium/software-rendering WebGL context-loss/restore
  cycle, unrelated to the asset). `npm run check` passes.

  New renders saved under `pipeline/.build/_review/` (standalone corner:
  `corner_0..3.png`; full Mule: `mule_0..3.png`; seam close-ups:
  `seam_3q_L.png`, `seam_3q_R.png`, `seam_side_R.png`; in-engine Babylon
  screenshot: `mule_babylon_screenshot_v2.png`).

  **Independently re-verified, not just read:** rebuilt the roster myself
  and confirmed via direct `GetExtentAttr()` queries — `Rim` now spans
  local X `[-0.13, 0.13]` vs. `Tire`'s `[-0.11, 0.11]` (protrudes 0.02 past
  both faces, as designed), and `CabGreenhouse`/`CargoBox` both span world
  X `[-0.93, 0.93]` with matching Y tops (flush, no mismatch). Rendered the
  standalone front corner and the full Mule myself (fresh renders, not the
  session's own) — the corner unambiguously reads as a wheel with a fender
  now, and the cab/cargo-box seam is a single continuous panel. `usdchecker`
  clean, `npm run check` passes, `main.ts` diff empty, no stray throwaway
  scripts. **Approved.** Committing to `feat/phase3-vehicle-roster` now (no
  PR yet — Phase 3's policy is one PR once 4a+4b+4c all land).

- **2026-09-07 — Phase 3c (`phase3c-goat-reuse-proof.md`): Approved, no
  changes requested.** Independently re-verified rather than trusting the
  report. **Structural reuse confirmed**: `build_goat()` calls the same
  `vehicle_utils` functions `build_mule()` uses (`build_wheel_corner`,
  `build_hull_section`, `build_window_band`, `add_door_hinge`,
  `add_cargo_latch`, `build_bumper`, `build_headlight`, `build_mirror`) with
  Goat-specific parameters — no forked/duplicated geometry-authoring code;
  the two genuinely new functions (`build_roll_bar`, `build_brush_guard`)
  live in the shared kit, not inline.
  **Suspension-strut fix (Task 1) confirmed numerically on both vehicles**,
  not just visually: computed each corner's strut/mount-cap world-space top
  via the full local-to-world transform chain (accounting for the corner's
  own xformOps *and* the reference-time wheel placement) — Mule's strut top
  lands at world `Y=0.920` against its own `deck_y=0.92`, Goat's at
  `Y=1.150` against `deck_y=1.15`, both essentially exact, with the mount
  cap overlapping ~0.025 into the body by design (avoids a hairline gap,
  same reasoning as the Mule's earlier cargo-box/greenhouse overlap fix).
  Rendered both standalone wheel corners and both full vehicles myself: the
  struts now read as tucked into the wheel arch with a small visible mount
  plate, not floating poles poking through the roofline.
  **Tailgate hinge generalization (Task 2) confirmed structurally and
  visually**: `Tailgate_Hinge` authors only a translate op at rest (no
  rotate yet, correct for a closed default pose), its door panel offset
  `(0, 0.125, 0)` — along Y, not X, confirming the `hinge_axis="X"`
  code path engaged correctly (Y-offset = half the tailgate's own height,
  matching a bottom-hinged panel) — and the session's own
  `goat_tailgate_open.png` render shows it swinging down correctly on a
  horizontal hinge, distinct from the Mule's vertical barn-door swing,
  confirmed via the same underlying function.
  **Visual differentiation** confirmed by render: open bed with visible
  side rails vs. the Mule's enclosed box, shorter single cab, wider knobby
  tires, olive/tan paint, a roll bar and brush guard that read clearly as
  off-road hardware — unmistakably a different vehicle at a glance, not a
  reskinned Mule.
  `usdchecker` clean on all 6 assets (both vehicles, both pairs of wheel
  corners); `TieDown_01..04` on the Goat's open bed use the same
  `cargo_utils` constants as the Mule's; `main.ts` diff empty; `npm run
  check` passes; no stray throwaway scripts. **Approved.** All three
  Phase 3 sub-prompts (4a/4b/4c) are now approved — opening the PR next.

- **2026-09-07 — Post-approval fix (PR #6, still open): collision hulls
  z-fighting against the visible body.** Found by the user opening the
  merged-pending Mule/Goat directly in Blender (not through the pipeline's
  own renders, which never showed it) — the Goat's body had a mottled,
  camo-like flicker on its rear section that turned out to be two opaque
  surfaces occupying nearly the same space. Confirmed by direct bounding-box
  query: the Mule's `Hull_CargoBox` was byte-for-byte identical to
  `CargoBox`'s own bounds, and the Goat's `Hull_Chassis` substantially
  overlapped `CabLower`/`CabGreenhouse` — a general pattern across every
  collision hull built so far, not Goat-specific. Root cause: this
  pipeline's collision meshes are deliberately left fully visible in
  USD/glTF (per the `usd-vehicle-assembly` skill — hiding them is meant to
  be a Babylon-side runtime decision that doesn't exist yet), so opening
  the raw asset in any DCC tool renders the hull directly superimposed on
  the body it's meant to approximate.
  **Fix:** added `vehicle_utils.add_collision_hull` — insets every hull by
  a small margin (`0.03m`) so it's always strictly inside the visible mesh,
  never coincident with or larger than it, and gives it an unmistakable
  debug color (bright magenta) so it reads as "collision proxy" rather than
  "broken paint" when inspected directly. Both vehicles' inline
  `make_box_mesh` hull calls replaced with this helper. Verified: rebuilt
  both vehicles, confirmed via bounding-box query that hulls are now
  strictly inset (not just visually), re-rendered the Goat and confirmed
  the mottled artifact is gone entirely (replaced by a clean, obviously
  intentional magenta volume visible through the open cab/bed, since this
  pipeline's body panels are thin shells with no modeled interior).
  `usdchecker` clean on both vehicles; `npm run check` passes. Committed
  directly to `feat/phase3-vehicle-roster` (PR #6 still open, not yet
  merged) rather than as a new prompt — a small, mechanical, well-scoped
  fix, not an asset-quality judgment call.
