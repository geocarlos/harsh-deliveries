> **Superseded, 2026-09-07 — do not run this prompt.** The session that ran
> this produced a vehicle built entirely from axis-aligned boxes/cylinders
> (chassis as one flat slab, cargo box as one shoebox), which read as "a
> poorly designed toy" on review (see `docs/prompts/INDEX.md`'s Review Log
> for the full account, including rendered before/after images). Rather than
> patch that draft, the vehicle-kit approach was redesigned around
> profile-extruded hull geometry and USD-referenced shared sub-assemblies,
> informed by a separate reference project
> (`modular-tank-learning-project`). See `phase3a-shared-vehicle-kit.md`,
> `phase3b-mule.md`, and `phase3c-goat-reuse-proof.md` for the plan that
> replaced this one. Kept here, unedited below, per this log's own
> append-don't-rewrite convention — not because any of it should be
> followed.

---

# Prompt — Phase 3a: Shared Vehicle Kit & Reference Vehicle (the Mule)

Paste this whole file as your first message in a **new** Claude Code session
opened at the repo root. That session has no memory of any prior session —
everything it needs is either in this file or in files it points to.

This is **half of roadmap Phase 3** (an addendum split by this prompt log,
not the roadmap itself — see `docs/prompts/INDEX.md`'s "Branching & merging"
section): this prompt builds the shared vehicle kit and proves it on one
reference vehicle, the Mule. Phase 3b (a separate prompt, written after this
one is reviewed) assembles the remaining four vehicles from the kit this
prompt validates. Both land on the same branch, `feat/phase3-vehicle-roster`.

## Context to read first

1. `CLAUDE.md` (repo root) — already auto-loaded; the Development Rules and
   Babylon.js Engine Rules sections matter directly here.
2. `docs/architecture/asset-roadmap.md` — read in full, but this prompt only
   asks you to execute the **first half** of **§3 "Phase 3"** (§1.1 Vehicles,
   §2.2 Rig scope, §2.3 Hardpoints, §2.5 Collision). Do not assemble Goat,
   Needle, Bastion, or Wasp — that's Phase 3b, a separate prompt, and it
   depends on this one's kit being stable first.
3. `docs/game-design/02-character-and-vehicle-design.md` §4.1 (The Mule) —
   the vehicle's actual design brief.
4. **A doc inconsistency to resolve, not replicate:** roadmap §2.2's worked
   code example names the cargo-latch pivot `CargoLatch_Hinge`, but the
   very next paragraph declares `_Latch` as its own required suffix in the
   fixed set (`_Steer`/`_Spin`/`_Hinge`/`_Latch`), and Phase 0's already-
   shipped `rig_utils.add_pivot_xform` validates against exactly that
   four-suffix set with `_Latch` as real and distinct from `_Hinge`. Use
   `_Latch` for the cargo latch pivot (e.g. `CargoLatch_Latch`) — the
   worked example's literal name is a copy-paste slip in the doc, not the
   intended convention; a latch and a hinge are different mechanisms
   (CLAUDE.md calls latches out as their own thing) and both suffixes exist
   in Phase 0's validated set precisely so they don't collapse into one.
5. `pipeline/rig_utils.py`, `pipeline/usd_utils.py`, `pipeline/manifest_utils.py`,
   `pipeline/export_utils.py`, `pipeline/cargo_utils.py` — every helper and
   convention from Phases 0–2, all merged to `main`. In particular:
   - `cargo_utils.PALLET_LENGTH`/`PALLET_WIDTH`/`TIE_DOWN_INSET` — the
     vehicle bed's `TieDown_01..04` **must** reuse these same constants
     (import them, don't re-derive new numbers), since §1.1/§1.7's whole
     point is that a cargo container's pallet and a vehicle bed's tie-downs
     share one footprint convention so either can mount the other.
   - `usd_utils.asset_slug`/`asset_output_paths` — the output-naming
     convention every asset from Phase 2 on uses.
6. `pipeline/build_cargo.py` — the closest existing precedent for this
   phase's `build_vehicles.py` structure (a variants list/dict driving a
   per-asset build function); Phase 3b will extend the same file, so
   structure it with that extension in mind (e.g. a `VEHICLE_VARIANTS` list
   with only the Mule populated) rather than something Mule-specific that'd
   need refactoring.

## Before you start

```
git checkout main
git pull --ff-only
git checkout -b feat/phase3-vehicle-roster
```

## Task 1 — Shared vehicle kit (`pipeline/vehicle_utils.py`)

Build each of these as a **generic, parametrized** function — this prompt
only exercises them for the Mule's stats, but Phase 3b calls the same
functions with different parameters for the other four vehicles, not forks
or copies of them:

- **Chassis frame builder** — parametric box-rail frame, scaled by
  length/width/height (and, loosely, plating-thickness for the Durability
  axis) rather than hardcoded per vehicle.
- **Wheel assembly kit** — one function producing a wheel at a given
  position, parametrized by tire radius/width and a steerable flag:
  - Steerable (front): `add_pivot_xform(rig, f"Wheel_{corner}", "_Steer")`,
    then nest `add_pivot_xform(<that prim>, f"Wheel_{corner}", "_Spin")`
    under it, matching Phase 1's validated two-level chain exactly.
  - Fixed (rear): a bare `_Spin` pivot only, no `_Steer` parent — matching
    Phase 0's original single-level pattern.
  - The tire mesh itself: `make_cylinder_mesh(..., axis="X")` so its round
    face points sideways (a wheel's rolling axis is lateral, matching the
    `_Spin` pivot's `rotateX`) — parametrize tread style loosely (e.g. tire
    width) even though this prompt only needs "road tire" for the Mule;
    Phase 3b needs "off-road knobby" and "motorcycle" variants from the
    same function.
- **Suspension mount/strut** — a simple visual strut/spring between chassis
  and wheel pivot, parametrized by a travel-length value (Mule: moderate;
  the roadmap notes Goat needs long travel and Bastion needs stiff/short —
  Phase 3b will pass different values, this prompt just needs the parameter
  to exist and read sensibly for the Mule's own baseline).
- **Cargo bed/box kit** — this prompt only needs the **enclosed box**
  variant (Mule); still write it as one of several archetype functions in
  this file (open bed, enclosed box, armored box, trunk, sidecar hauler)
  with only enclosed-box implemented now and the others stubbed/left as
  Phase 3b's job — the point is the file's shape shouldn't need
  restructuring when Phase 3b adds them. The enclosed box authors its own
  `TieDown_01..04` via `cargo_utils`' shared pallet-footprint constants (see
  Context item 5).
- **Door/hatch hinge kit** — a `_Hinge` pivot + door mesh (Mule: rear
  doors).
- **Cargo latch kit** — a `_Latch` pivot (see Context item 4) + small latch
  mesh, reused wherever a cargo bay closes.
- **Lighting & marker kit** — headlight/taillight geometry (small
  box/cylinder, front/rear) and a livery/decal attach point (a flat quad or
  shallow box with a distinct material color per vehicle's Profile axis) —
  no texture painting needed yet, per the roadmap.

## Task 2 — Assemble the Mule

Write `pipeline/build_vehicles.py` (structured per Context item 6):

- Category `"Vehicle"`, name `"Mule"`.
- Chassis sized at van scale (large enclosed cargo box, per Module 2 §4.1:
  Cargo Care+, Capacity+, Traction−).
- 4 wheels: front pair steerable (road tire), rear pair fixed (road tire).
- Suspension struts at all 4 wheel positions.
- Enclosed cargo box on the rear, with `TieDown_01..04` matching
  `cargo_utils`' footprint, a rear door on a `_Hinge` pivot, and a cargo
  latch on a `_Latch` pivot.
- Headlights, taillights, one livery attach point with a distinct paint
  color.
- `Collision/Hull_*` proxy geometry (§2.5) — at minimum a chassis hull;
  add wheel hulls too if that reads as necessary for a physics impostor to
  make sense, your judgment, but something must exist under `Collision`
  for every vehicle, non-negotiably (the roadmap treats this as load-bearing
  for Cargo Integrity, not deferrable polish).
- `Hardpoints/DriverSeat` (in-cab, sensible seat height) and
  `Hardpoints/ExitPoint` (just outside the driver's door, ground level).
- Export via `asset_output_paths(MODELS_DIR, "Vehicle", "Mule")`, same
  `.usdz`/`.glb`/manifest pattern as Phase 2's build scripts (no gameplay
  metadata is strictly required on the Mule yet, but keep the pattern
  available/consistent if you do add any).

## Task 3 — Babylon validation

Using the `run` skill (or `npm run dev` + a real browser): load the Mule's
`.glb`, confirm zero console errors, then temporarily add a test snippet to
`src/main.ts` (same throwaway pattern as Phase 1) that finds nodes by suffix
and drives them:

- Rotate a `_Steer` node and confirm the front wheel visibly turns about a
  **vertical axis at the wheel's own position**, not the chassis's origin.
- Rotate/spin a `_Spin` node and confirm it rolls about its own **lateral**
  axis, at its own position.

Remove the snippet from `main.ts` before finishing, per the same rule as
every prior phase's throwaway runtime probes.

## Task 4 — Anchor/DriverSeat validation (Mule only; full-roster check is Phase 3b's job)

Take one Phase 2 placeholder character (any of the 6) and confirm its
`Anchor` hardpoint aligns onto the Mule's `Hardpoints/DriverSeat` by pure
translation (no per-vehicle special-casing), the same check Phase 2 did
against a stand-in marker — this time against a real vehicle. Throwaway
script; report whether kept or removed.

## Acceptance criteria (adapted from the roadmap; full 5-vehicle criteria apply once Phase 3b lands)

- The Mule exports a clean `.usdz`/`.glb` pair with `_Steer`/`_Spin`/
  `_Hinge`/`_Latch` pivots present and correctly parented (mesh is always a
  child of its pivot).
- Babylon-side steering/rolling test (Task 3) passes visually.
- `usdchecker` clean; `Collision/Hull_*` present.
- `DriverSeat`/`ExitPoint` present at sensible positions; the Task 4
  alignment check passes.
- The vehicle bed's `TieDown_01..04` land at the exact same relative
  footprint as `cargo_utils`' pallet convention (verify numerically, not
  just "looks about right").
- `npm run check` passes; no leftover throwaway code committed.

(Cross-vehicle silhouette distinguishability and the "one character aligns
onto every vehicle without special-casing" full-roster checks are Phase 3b's
acceptance criteria, not this prompt's — only one vehicle exists after this
one.)

## What to report back

- Final shape of `pipeline/vehicle_utils.py`: every kit function's
  signature, and which parameters Phase 3b will need to vary per vehicle
  (tire style, chassis scale, suspension travel, bed archetype, etc.) —
  this is the most important thing to get right for Phase 3b's prompt.
- Confirmation of the tie-down footprint match against `cargo_utils`'
  constants (numeric, not visual).
- The Babylon steer/spin test's result.
- Whether Task 4's throwaway script was kept or removed.
- Any deviation from this prompt, and anything that felt awkward or
  under-specified about the kit's shape that Phase 3b's author should know
  before writing that prompt.

Do not assemble Goat, Needle, Bastion, or Wasp — that's Phase 3b, a separate
prompt. Stop after this prompt's acceptance criteria are met and report back.
