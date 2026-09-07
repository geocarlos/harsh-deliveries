# Prompt — Phase 0: Core OpenUSD Utility Library

Paste this whole file as your first message in a **new** Claude Code session
opened at the repo root. That session has no memory of how this prompt was
written — everything it needs is either in this file or in files it points to.

## Context to read first

1. `CLAUDE.md` (repo root) — already auto-loaded as project instructions;
   re-skim it anyway, this phase touches the Asset Pipeline and OpenUSD
   Coding Guidelines sections directly.
2. `docs/architecture/asset-roadmap.md` — read in full for orientation, but
   this prompt only asks you to execute **§3 "Phase 0"** (and the parts of
   §1/§2 it references: §2.1 root structure, §2.2 rig naming convention,
   §2.3 hardpoints, §2.4 metadata strategy). Do not start Phase 1 work
   (customData-vs-glTF-extras validation) — that's a separate prompt.
3. `pipeline/usd_utils.py` and `pipeline/export_utils.py` — the existing
   helpers you're extending, not replacing. Read both fully before writing
   anything; the new helpers should match their existing conventions
   (explicit `UsdGeom.Mesh` not implicit Gprims, one cached material per
   `(stage, color)`, flat per-face normals, etc.) rather than reinventing them.

## Task

Build the Phase 0 helper library. No production assets, no Phase 1+ scope.

### 1. `pipeline/rig_utils.py` — new file

- `add_pivot_xform(parent, name, suffix, translate=(0, 0, 0))`
  - Creates a child `UsdGeom.Xform` named `f"{name}{suffix}"` under `parent`.
  - **Validate `suffix`** against the fixed set from roadmap §2.2:
    `_Steer`, `_Spin`, `_Hinge`, `_Latch`. Raise on anything else — this
    suffix set is load-bearing for the Babylon runtime's future
    lookup-by-suffix pattern (§2.2), so silently accepting a typo'd suffix
    is exactly the kind of drift that's worse than a hard failure here.
  - Author the `translate` as a translate op if non-zero; return the `Xform`
    (or its `Prim`) so the caller can parent a mesh under it and add a
    rotate op via the helper below.
- Rotate-op helper(s) for driving the pivot at author time (a fixed pose,
  not runtime animation — that's the Babylon side's job) and, more
  importantly, for authoring the pivot's rotate op with the *right axis and
  op ordering* so the transform survives the glTF round-trip correctly.
  Cover the axes the roadmap's worked example (§2.2) actually uses:
  steering = rotateY, wheel spin = rotateX, door hinge = rotateY, latch
  flip = rotateX — but make the axis a parameter, not hardcoded per suffix,
  since a future hinge (e.g. a horizontal gate-arm in Phase 5) may need a
  different axis than a vertical door. Suggested shape:
  `set_pivot_rotation(pivot_prim, axis, degrees=0.0)` where `axis` is one of
  `"X"/"Y"/"Z"`.
- Keep `Wheel_FL_Steer` → child `Wheel_FL_Spin` → child `Wheel_FL_Mesh`
  nesting (pivot is always the parent of the mesh it moves, never a
  sibling) achievable cleanly with these two helpers together — don't
  build a separate all-in-one "wheel assembly" helper here, that belongs to
  Phase 3's vehicle-specific kit, not this generic library.

### 2. Hardpoint helper — add to `rig_utils.py` or a new `pipeline/hardpoint_utils.py`, your call

- `add_hardpoint(parent, name, translate)` — a zero-geometry child `Xform`
  (translate-only, no mesh, no rotate) under `parent`, named exactly `name`
  (caller passes the full name, e.g. `"TieDown_01"`, `"DriverSeat"`,
  `"ConnectOut"` — this helper doesn't invent naming conventions, it just
  authors the marker).

### 3. UV mapping — extend `pipeline/usd_utils.py`

- Add `primvars:st` authoring to both `make_box_mesh` and `make_cylinder_mesh`.
  Per-face-varying (matching the existing flat-normals convention) is
  probably simplest given these are hard-surface boxes/cylinders, not smooth
  organic meshes — but use your judgment and note the choice.
- Add a `make_mesh` variant (or an optional parameter on the existing
  `make_mesh`) that accepts explicit UV coordinates for hand-authored
  geometry that isn't a box or cylinder.
- These UVs only need to be valid, not art-directed — Phase 0's acceptance
  criteria is `usdchecker`'s primvar checks passing, not correct texel
  density.

### 4. Material palette extension — extend `pipeline/usd_utils.py`

- `get_material`/`set_color` currently key purely on flat `color` (RGB) via
  `UsdPreviewSurface.diffuseColor`. Extend so a caller can also specify a
  **preset** that maps to roughness/metallic values on the same
  `UsdPreviewSurface` shader — enough presets to cover the roadmap's stated
  near-term needs: `paint` (vehicle livery), `rubber` (tires), `glass-preview`
  (Cargo's glass case — this is a placeholder preview material, not real
  glass/transmission, since `UsdPreviewSurface` doesn't have to nail
  physically-correct transparency here), `unmarked-matte` (sealed/illegal
  cargo container), `steel` (drums, machine-parts crate, armor plating).
  Keep backward compatibility with existing `get_material(stage, color)`
  call sites (Phase 0 shouldn't break anything that already calls the
  current 2-arg form) — e.g. an optional `preset="paint"` parameter
  defaulting to whatever the current behavior effectively is.
- The material cache key (`(id(stage), color)`) needs to become
  `(id(stage), color, preset)` or equivalent, so the same color in two
  different presets doesn't collide.

### 5. `pipeline/manifest_utils.py` — new file

- `write_manifest(path, data)` — writes `data` (a plain dict) as pretty JSON
  to `path`. This is the sidecar-manifest fallback described in roadmap
  §2.4, built now so it's ready regardless of which way Phase 1's
  customData-survival test resolves. Don't wire it into any asset script
  yet — that's Phase 1/2's job once the metadata-channel decision is made.

### 6. `create_asset_stage(category, name)` — extend `pipeline/usd_utils.py`

- Wraps the existing `create_stage()` to produce the roadmap §2.1 scope
  skeleton consistently:
  ```
  /<Category>_<AssetName>          Xform, default prim
    /Geometry                      Scope
    /Rig                           Scope
    /Hardpoints                    Scope
    /Collision                     Scope
    /Materials                     Scope
  ```
- `category` should be validated against the fixed set from §2.1: `Vehicle`,
  `Cargo`, `Terrain`, `Hazard`, `Prop`, `Character` — same reasoning as the
  pivot-suffix validation above (this is a naming contract other tooling
  will rely on later, so fail loudly on a typo rather than silently
  authoring `/Vehcile_Mule`).
- Return whatever shape is most useful to callers — e.g. the stage plus a
  dict/namedtuple of the five scope prims — your call, but document it in
  the docstring since every later phase's asset scripts will call this.
- Figure out where the file path this writes to should live for a *test*
  asset (see Acceptance Criteria below) — production asset scripts calling
  this in later phases will pass their own path under `pipeline/.build/`
  (already gitignored), same as today's `create_stage()` callers presumably
  do.

## Acceptance criteria (from the roadmap, verbatim)

- A trivial hand-written test asset — one box "chassis," one box "wheel" on
  a `_Spin` pivot, one `TieDown_01` hardpoint — builds via the new helpers
  only (i.e. write a short throwaway script under `pipeline/` that exercises
  `create_asset_stage`, `add_pivot_xform`, `add_hardpoint`, `make_box_mesh`,
  `set_color`). Output to `pipeline/.build/` (gitignored).
- `usdchecker` clean on the flattened output. (Use `export_utils.export_usdz`
  or just `stage.Flatten()` + `usdchecker` directly on the flattened layer —
  no need to produce a real `.usdz`/`.glb` pair for this throwaway test asset,
  that round-trip is Phase 1's job.)
- `usdtree` (or equivalent stage traversal) shows the exact §2.1/§2.2/§2.3
  scope structure — confirm the `_Spin` pivot is the *parent* of the wheel
  mesh, not a sibling.
- UV primvars present and valid (`usdchecker`'s primvar-related checks pass)
  on a textured test box.

## What to report back

When done, summarize in your final message (this is what gets reviewed
before Phase 1's prompt is written):

- Final function signatures for everything in the Task list above, and
  where each lives (file + line).
- Any place you deviated from what this prompt specified, and why.
- The exact `usdchecker` output (or confirmation it was clean) and the
  `usdtree` output for the test asset.
- Whether the throwaway test script was left in the repo or deleted — per
  CLAUDE.md's general practice and the roadmap's Phase-verification gates,
  a throwaway validation script should probably not be committed as
  production code once it's served its purpose, but flag your reasoning
  either way rather than assuming.
- Any open questions or judgment calls you had to make that the next
  phase's author (a different, fresh session) should know about.

Do not proceed into Phase 1 work (the export round-trip / Babylon load /
customData-survival test) — stop after Phase 0's acceptance criteria are met
and report back.
