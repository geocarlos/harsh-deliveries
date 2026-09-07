# Prompt — Phase 1: Basic Test Prims & Build Pipeline Validation

Paste this whole file as your first message in a **new** Claude Code session
opened at the repo root. That session has no memory of how this prompt was
written, or of Phase 0's session — everything it needs is either in this
file or in files it points to.

## Context to read first

1. `CLAUDE.md` (repo root) — already auto-loaded as project instructions;
   the Asset Pipeline and Babylon.js Engine Rules sections matter directly
   for this phase.
2. `docs/architecture/asset-roadmap.md` — read in full for orientation, but
   this prompt only asks you to execute **§3 "Phase 1"**, resolving the
   open risk flagged in **§2.4 "Metadata strategy"**. Do not start Phase 2
   work (production cargo/prop/character assets) — that's a separate prompt,
   and it depends on the decision this phase makes.
3. `pipeline/rig_utils.py`, `pipeline/usd_utils.py`, `pipeline/manifest_utils.py`
   — Phase 0's helpers (merged to `main` in PR #3), which this phase's test
   asset must be built from, not new one-off code.
4. `pipeline/export_utils.py` — the `export_usdz`/`export_gltf` functions
   you're exercising end-to-end for the first time in this codebase.
5. `pipeline/build_assets.py` — the existing sample pipeline entry point;
   read it for the pattern (author under `pipeline/.build/`, export to
   `public/assets/models/`), but don't modify it — write a new throwaway
   script instead (see Task 1 below).
6. `src/main.ts` — the Babylon runtime. Note it already does
   `AppendSceneAsync('/assets/models/model.glb', scene)` by default, and
   `public/assets/models/*` is gitignored (except `.gitkeep`) — so this
   phase's test export can write directly to `model.glb`/`model.usdz`
   without touching `main.ts`'s asset path or needing to revert anything.
7. Skim the `usd-dcc-export` Claude skill (invoke it, or ask about its
   content) for its §5 "headless Blender as a diagnostic tool" pattern and
   its known-gaps list (PointInstancer, displayColor-only shading,
   implicit-Gprim bindings) — not all directly relevant here, but it's the
   skill this exact validation question was flagged against.

## Before you start

```
git checkout main
git pull --ff-only
git checkout -b feat/phase1-pipeline-validation
```

Confirm Blender is actually invocable before relying on `export_gltf()` —
`BLENDER_EXECUTABLE` env var or `blender` on `PATH` (see
`export_utils._find_blender_executable`). This phase is the *first* time
this codebase's `export_gltf()` path actually runs end-to-end — if Blender
isn't set up in this environment, stop and report that as a blocker rather
than working around it.

## Task

This phase is a **spike** — its output is a validated pipeline and a
recorded decision, not a production asset. Nothing built here should ship
as game content.

### 1. Build one minimal articulated test asset

Write a throwaway script (e.g. `pipeline/phase1_test_asset.py`, not
committed at the end — see "What to report back") using **only** Phase 0's
helpers:

- `create_asset_stage(path, "Vehicle", "Phase1Test")` (or whichever category
  reads best — `"Vehicle"` fits a chassis+wheel+door shape).
- A box chassis mesh in `Geometry`.
- A **nested** wheel pivot chain in `Rig`, matching the roadmap's §2.2
  worked example exactly: `add_pivot_xform(rig_scope, "Wheel_FL", "_Steer")`,
  then `add_pivot_xform(<that prim>, "Wheel_FL", "_Spin")`, then a wheel box
  mesh parented under the `_Spin` pivot. (Phase 0's own test asset only
  exercised a bare `_Spin` — this phase is the first to prove the two-level
  `_Steer`→`_Spin` nesting round-trips correctly.)
- A `_Hinge` pivot in `Rig` (e.g. `Door`) with a door-panel box mesh parented
  under it.
- `add_hardpoint(hardpoints_scope, "TieDown_01", translate=(...))`.
- **One `customData` attribute** on some prim (your choice which — the
  `TieDown_01` hardpoint or the chassis both make sense), authored via
  `prim.SetCustomDataByKey("harshDeliveries:testValue", <some value>)`, per
  roadmap §2.4's namespace convention.
- Export to `public/assets/models/model.usdz` and `model.glb` via
  `export_utils.export_usdz`/`export_gltf` (these paths are what `main.ts`
  already loads by default, and they're gitignored build output, so
  overwriting the existing sample cube here is fine).

### 2. Validate the USD side

- `usdchecker` clean on the flattened layer (same pattern as Phase 0).
- `usdtree` confirms the pivot-parents-mesh structure for both the
  `_Steer`→`_Spin` chain and the `_Hinge`, and that `TieDown_01` and the
  `customData` attribute are present.

### 3. Inspect the exported `.glb` directly

A `.glb` is a binary container: a 12-byte header followed by chunks, the
first of which is a JSON chunk (glTF's scene/node/mesh graph). Parse that
JSON chunk directly (Python's `struct`, or any GLB-aware library already
available in this environment) and answer, concretely:

- **Node names:** do `Wheel_FL_Steer`, `Wheel_FL_Spin`, `Door_Hinge`, and
  `TieDown_01` survive as glTF node `name` fields? Exactly, or sanitized
  (e.g. characters replaced)? Record the exact before/after string for each.
- **Hierarchy:** is each pivot node still the *parent* of the mesh node it
  should move, per the glTF node `children` arrays — not a sibling, and not
  collapsed away?
- **`extras`:** does any node in the glTF JSON carry an `extras` object with
  `harshDeliveries:testValue` (or however Blender's exporter chose to
  represent it, if at all)? This is the specific unverified claim roadmap
  §2.4 flags — record the raw JSON for that node's `extras` field (or its
  absence) verbatim in your report, not just a yes/no.

### 4. Load in the actual Babylon runtime and prove the naming-lookup strategy

Use the `run` Claude skill (or `npm run dev` + a real browser) to launch the
app and confirm the `.glb` renders with **zero console errors**.

Then, temporarily, add a small test snippet to `src/main.ts` (after the
`AppendSceneAsync` call) that finds a node whose name ends in `_Spin` —
however that name actually came through per Task 3's finding, sanitized or
not — via Babylon's scene graph (e.g.
`scene.transformNodes.find(n => n.name.endsWith('_Spin'))` or
`scene.getTransformNodeByName(...)`) and rotates it (either a one-shot
rotation you confirm visually, or a per-frame increment in the render loop —
whichever makes it easiest to see it's rotating about the wheel's own
position, not the chassis's origin). Confirm visually, then **remove this
snippet from `main.ts` before finishing** — it's a throwaway validation
probe, not runtime feature code (same rule as the pipeline-side throwaway
script).

### 5. Record the metadata-channel decision

Based on Task 3's `extras` finding, resolve roadmap §2.4's open question.
Update the **existing** bullet about this in `asset-roadmap.md`'s
"Decisions Log" section (the one that currently says the decision is "left
as a Phase-1-validated decision, not asserted here") — append the actual
finding to it rather than deleting/rewriting it, matching the document's own
stated convention ("prefer a short addendum noting what changed and why over
editing this file's history in place"). State plainly which of the two
paths wins:

- customData survives as glTF `extras`, readable from Babylon's loaded node
  data → author gameplay metadata directly via `customData` going forward,
  `manifest_utils.write_manifest` stays built-but-unused.
- customData does **not** survive → the sidecar manifest
  (`manifest_utils.write_manifest`) becomes the required path for Phase 2+
  asset scripts; every future asset script should call it alongside its
  `.glb`/`.usdz` export.

## Acceptance criteria (from the roadmap, verbatim, plus the common gates)

- `.glb` loads and renders in the Babylon dev server (`npm run dev`) with
  zero console errors.
- The `_Spin` pivot rotates correctly about its intended axis when driven
  from the throwaway runtime test script (removed afterward, per Task 4).
- A written finding on customData/extras survival exists in
  `asset-roadmap.md`'s Decisions Log (Task 5) — Phase 2+ metadata authoring
  depends on knowing which path to use.
- `npm run check` passes, with no leftover throwaway runtime code from
  Task 4 committed.
- Also clear the roadmap's §4 common gates: `usdchecker` clean; `usdtree`
  hierarchy correct (pivot is parent, not sibling); naming-convention
  compliance (`_Steer`/`_Spin`/`_Hinge`/`TieDown_NN`) confirmed both in USD
  and in the exported glTF node names per Task 3.

## What to report back

- The exact node-name survival table from Task 3 (USD name → glTF node
  name, one row per pivot/hardpoint).
- The raw `extras` finding (JSON snippet or explicit absence) and which way
  you resolved the metadata-channel decision.
- Confirmation the Babylon dev-server render was clean (paste the console
  output or screenshot description) and that the `_Spin` lookup-and-rotate
  probe worked, rotating about the wheel's own pivot position.
- Whether `pipeline/phase1_test_asset.py` and the `main.ts` test snippet
  were both removed before finishing (they should be — flag if you kept
  either, and why).
- Any deviation from this prompt, and any open question the Phase 2
  prompt's author should know about.

Do not proceed into Phase 2 work (cargo/prop/character production assets) —
stop after this phase's acceptance criteria are met and report back.
