# Prompt — Phase 2: Modular Cargo & Prop Engine

Paste this whole file as your first message in a **new** Claude Code session
opened at the repo root. That session has no memory of any prior session —
everything it needs is either in this file or in files it points to.

## Context to read first

1. `CLAUDE.md` (repo root) — already auto-loaded as project instructions.
2. `docs/architecture/asset-roadmap.md` — read in full, but this prompt only
   asks you to execute **§3 "Phase 2"** (and the parts of §1/§2 it depends
   on: §1.2 Cargo, §1.5 Props, §1.6 Runners/Characters, §2.1 root structure,
   §2.3 hardpoints, §2.4 metadata — **now resolved**, see next point).
3. `asset-roadmap.md`'s **Decisions Log**, specifically the Phase 1 addendum:
   USD `customData` does **not** survive the glTF export. `pipeline/manifest_utils.write_manifest`
   is the required metadata channel from this phase on — any gameplay value
   from the Cargo table below (Fragility, Legality) that needs to reach the
   runtime belongs in a manifest sidecar file, keyed by prim/node name, not
   `customData`.
4. `pipeline/usd_utils.py`, `pipeline/rig_utils.py`, `pipeline/manifest_utils.py`,
   `pipeline/export_utils.py` — Phase 0/1's helpers, all merged to `main`.
   Build from these, don't re-derive them.
5. `docs/game-design/02-character-and-vehicle-design.md` §2 — the 6 roster
   runners this phase needs placeholders for (names below).
6. `pipeline/build_assets.py` — the existing pattern for a pipeline entry
   point (author under `pipeline/.build/`, export both artifacts to
   `public/assets/models/`). This phase is the first to need **several**
   distinct named output assets rather than one generic `model.glb` — see
   Task 0 for the naming convention to establish now.

## Before you start

```
git checkout main
git pull --ff-only
git checkout -b feat/phase2-cargo-props-characters
```

## Task 0 — Output naming convention (establish now, applies to every phase after this one)

Every asset from this phase on needs its own output filename (not the
generic `model.usdz`/`model.glb` `build_assets.py` uses for its single
sample scene). Adopt: `public/assets/models/<category_lower>_<asset_name_snake>.usdz`
and `.glb` — e.g. `Cargo_WoodCrate` → `cargo_wood_crate.usdz`/`.glb`,
`Character_MaraItoh` → `character_mara_itoh.usdz`/`.glb`. Put this in a small
shared helper (e.g. `asset_output_paths(category, name)` in `usd_utils.py`)
rather than re-deriving the slugify logic per build script, since Phases 3–5
will call it too.

Unlike Phase 0/1's throwaway validation scripts, the build scripts you write
this phase (Task 1–4) **are** production pipeline code — real, committed
`pipeline/build_*.py` entry points in the same spirit as `build_assets.py`,
not one-off spikes.

## Task 1 — Cargo container kit (§1.2)

Build a shared `pipeline/cargo_utils.py`:

- A **pallet base** — pick one fixed footprint (e.g. a low box, ~1.2m x
  1.0m) and define its dimensions as named constants in this file, the same
  way Phase 4 will later need a single `TILE_LENGTH` constant for terrain —
  one source of truth, not a magic number repeated per container script.
- **Standard tie-down corners**: `TieDown_01`..`_04` via `rig_utils.add_hardpoint`,
  positioned at the pallet's four corners, inset slightly from the edge.
  These must land at the **same relative position on every container
  variant** (§2.3's point: a future loadout-assembly script matches these
  by name/count between a cargo prim and a vehicle bed prim, so positional
  consistency here isn't cosmetic).
- A **container shell kit** — one function per archetype (crate, drum,
  case, sealed box), differentiated by **silhouette + material only** (no
  unique rigging — cargo doesn't animate on its own):

  | Cargo profile | Fragility | Legality | Container archetype | Suggested material |
  |---|---|---|---|---|
  | Canned goods | Low | Legal | Wood crate | plain color (brown/tan), no dedicated "wood" preset exists yet — don't invent one unless you genuinely need to; a flat color read is enough per this phase's visual-differentiation check |
  | Glassware | High | Legal | Glass-panel case | `glass-preview` preset |
  | Machine parts | Medium | Legal | Metal parts crate | `steel` preset |
  | Undeclared/illegal cargo | Low (physical) | Illegal | Sealed unmarked container | `unmarked-matte` preset |
  | Volatile chemical drums | High | Illegal | Steel drum (banded) | `steel` preset, use `make_cylinder_mesh` |

- Write **`pipeline/build_cargo.py`**: authors all 5 variants (each its own
  `create_asset_stage("Cargo", <name>)`), exports each as its own `.usdz`/`.glb`
  pair per Task 0's convention, and writes a manifest sidecar per container
  via `manifest_utils.write_manifest` carrying that row's Fragility and
  Legality values, keyed by the container's own asset name.

## Task 2 — Multi-unit stacking test (§1.2, PointInstancer bake)

Read `export_utils.bake_point_instancer`/`bake_all_point_instancers` closely
before starting this — **the prototype prim a `PointInstancer` points at
must be sourced via an external reference**, not authored inline in the same
stage. `_prototype_source()` reads the prototype prim's `references`
metadata to find the source asset; an inline-authored prototype has no such
metadata and will fail at bake time. Consult the `usd-dcc-export` Claude
skill for this exact gotcha before writing the instancer.

- Build a small test stage that references one already-exported cargo
  container (e.g. the wood crate) as a `PointInstancer` prototype, stacked
  3–4 units high on one pallet.
- Bake via `export_utils.bake_all_point_instancers(stage, asset_root)`
  before export — confirm in the flattened/exported result that there is
  no leftover/duplicate/mispositioned geometry (the deactivated instancer
  should be inert, the baked instances correctly transformed).
- This can be a throwaway validation script (not a permanent
  `pipeline/build_*.py`) — it's proving the stacking pattern works, not
  shipping stacked-pallet as a named asset. Report whether you kept or
  deleted it and why.

## Task 3 — Prop kit (§1.5)

Write **`pipeline/build_props.py`**, authoring and exporting (own `.usdz`/`.glb`
pair per prop, category `"Prop"`):

- **Signage kit** — a simple flat/shallow-box sign geometry (dispatch-board
  flavor signage, regional graffiti/propaganda — differentiate via material
  color, not texture art, at this stage).
- **Wreckage** — author calmed vs. militarized as a `UsdVariantSet` on one
  asset (per §1.3's variant-set note), not two separate wreckage assets.
  This is the pipeline's first use of `UsdVariantSets` — Phase 4's biome
  dressing depends on the same pattern working, so it's worth surfacing any
  friction here rather than discovering it there.
- **Barricade / checkpoint booth** — static geometry only. The gate-arm
  hinge is explicitly deferred to Phase 5 (it needs the Phase 0 rig helpers
  exercised on a non-vehicle asset, which Phase 5 will do first at that
  point) — don't add a `_Hinge` pivot to the booth/barricade this phase.
- **Small clutter kit** (barrels, loose crates, debris) — reuse Task 1's
  container shell kit geometry where sensible (a "damaged crate" prop is a
  cargo crate mesh placed as static dressing, per §1.5) rather than
  authoring new crate geometry from scratch.

## Task 4 — Placeholder Character kit (§1.6)

Write **`pipeline/build_characters.py`**. One placeholder proxy per roster
runner, category `"Character"`, `Geometry` + a single `Hardpoints/Anchor`
marker only (no `Rig`, no `Collision` — per §2.1, those scopes stay
empty/unused until real character geometry replaces the placeholder):

- Mara Itoh, Diego Salvatierra, Kass Ferreira, Iveta Rusul, Ren Okafor-Boyle,
  and the wildcard sixth runner ("Warden" — no full name in the design docs
  yet, use `Character_Warden`).
- Pick **one** placeholder geometry approach (capsule mesh or billboard
  card) and apply it consistently across all 6 — don't mix. A plain capsule
  with a distinct `set_color` per runner is the simpler route (no texture
  asset needed at all, and the roadmap explicitly allows a flat placeholder
  color in place of real portrait art) — use your judgment, but justify
  whichever you pick in your report.
- **Anchor-alignment validation** (required before Phase 3 commits to
  authoring `DriverSeat` on every vehicle): build one throwaway test — a
  stand-in `DriverSeat` marker Xform at some arbitrary world position (not a
  full vehicle asset), then position one character placeholder so its
  `Anchor` hardpoint's world position matches that marker exactly. Confirm
  numerically (compare world-space positions via USD API) or visually in
  `usdview`/a Blender screenshot. This proves the anchor-matching contract
  (§2.3) holds before it's relied on at vehicle-roster scale. Throwaway —
  report whether you kept or deleted this script.

## Acceptance criteria (from the roadmap, verbatim)

- Every cargo container type exports a clean `.usdz` + `.glb` pair;
  `TieDown_01..04` hardpoints present and positioned consistently across
  all container variants.
- The stacked-pallet test asset's baked instances are visually correct in
  Blender (no leftover/duplicate/mispositioned geometry) and in the
  Babylon-loaded `.glb`.
- Visual differentiation check in a read-only viewport (`usdview` or
  Blender): glass reads as distinct from steel drum reads as distinct from
  wood crate, using only the Phase 0 material-preset extension (no texture
  painting required).
- All 6 placeholder character proxies export clean `.usdz`/`.glb` pairs with
  an `Anchor` hardpoint present; the anchor-alignment validation (Task 4)
  confirms the approach before Phase 3 commits to it fleet-wide.
- Also clear the roadmap's §4 common gates: `usdchecker` clean on every
  asset; naming-convention compliance (`TieDown_NN`, `Anchor`); no stray
  deactivated-vs-invisible geometry from the `PointInstancer` bake;
  `npm run check` still passes.

## What to report back

- Final file layout: every new `pipeline/*.py` file and what it produces.
- The output-naming convention you landed on for Task 0, if it differs from
  this prompt's suggestion.
- Which placeholder geometry approach you chose for characters, and why.
- Confirmation of the anchor-alignment validation's numeric/visual result.
- Confirmation of the `PointInstancer` bake's cleanliness (no leftover
  geometry) and how you checked it.
- Whether Task 2's and Task 4's throwaway scripts were kept or removed.
- Any deviation from this prompt, and anything the Phase 3 prompt's author
  should know — especially anything about the pallet/tie-down convention or
  the manifest format that Phase 3's vehicle beds need to match exactly.

Do not proceed into Phase 3 work (vehicle chassis/rigging) — stop after this
phase's acceptance criteria are met and report back.
