# Prompt — Phase 3a (revised): Shared, Customizable Vehicle Kit

Paste this whole file as your first message in a **new** Claude Code session
opened at the repo root. That session has no memory of any prior session —
everything it needs is either in this file or in files it points to.

This supersedes an earlier Phase 3a attempt (`phase3a-vehicle-kit-and-mule.md`,
marked superseded at its top) that built a vehicle from plain axis-aligned
boxes/cylinders and, on review, read as "a poorly designed toy" — see
`docs/prompts/INDEX.md`'s Review Log entry for that phase for the full
account. This prompt builds **only the shared kit** — no full vehicle yet.
Phase 3b (a separate prompt, written after this one is reviewed) assembles
the Mule from it; Phase 3c assembles the Goat from the *same* kit with
different parameters, as the explicit proof the kit is genuinely reusable
and not secretly Mule-specific. All three land on `feat/phase3-vehicle-roster`.

**The user's own instruction driving this phase: trade speed for realism and
detail.** Do not rush this. A visually convincing result matters more than
finishing quickly.

## Context to read first

1. `CLAUDE.md` (repo root) — already auto-loaded; Development Rules and
   Babylon.js Engine Rules sections matter here.
2. `docs/architecture/asset-roadmap.md` — §1.1 (Vehicles), §2.2 (Rig scope),
   §2.3 (Hardpoints), §2.5 (Collision). This prompt is still building toward
   roadmap Phase 3's eventual acceptance criteria, just via a more capable
   kit than the roadmap's own text originally envisioned.
3. `docs/prompts/INDEX.md`'s Review Log — read the Phase 3a entry
   specifically (the rejected-and-redesigned one) for exactly what went
   wrong last time (flat-slab chassis, floating shoebox cargo box, visibly
   faceted 16-sided wheel cylinders) and what the follow-up prototyping
   (v2-v4, described in that entry) found actually fixed it: real vehicle
   anatomy (hood/cab/greenhouse/wheel-arches/bumpers), not just more boxes.
4. `pipeline/usd_utils.py`, `pipeline/rig_utils.py`, `pipeline/cargo_utils.py`,
   `pipeline/export_utils.py` — every existing helper and convention from
   Phases 0-2, all merged to `main`. Build on these; don't re-derive them.
5. **A separate reference project, read for technique, not copied
   verbatim:** `C:\Users\geocarlos\workspace\Geo\modular-tank-learning-project`
   — a prior session's OpenUSD tank build the user holds up as the quality
   bar. Read:
   - `src/chassis.py` — the technique that matters most here: the hull is a
     5-point 2D polygon **extruded across width**, not a box, giving a real
     sloped glacis plate and angled rear deck. Also note its clearly
     separated "hull details" section (headlights, hatch, exhaust, tow
     hooks, fenders) added *after* the core volume — a deliberate, separate
     detail pass, not folded into the main shape.
   - `src/turret_assembly.py` — a tapered frustum (bottom radius ≠ top
     radius) used for an angled, armored silhouette instead of a plain
     cylinder.
   - `src/track.py` + `src/master_assembly.py` — the compositional pattern:
     a part built as its own `.usda`, referenced (not re-authored inline)
     into an assembly, with a per-instance transform override. Note *why*
     the left/right track needs a 90-degree **yaw** (rotation) rather than
     a mirror: mirroring via negative scale flips face winding/normal
     direction (a rotation's determinant is +1; a mirror's is -1) — a real
     pitfall to design around, not copy.
   - This project's own `src/export_for_dcc.py` does *not* deactivate its
     copied `PointInstancer` bake template — the same leftover-geometry bug
     this project's Phase 2 review already caught and fixed in our own
     `export_utils.py`. Don't reintroduce it; nothing in this prompt should
     need to touch `export_utils.py` at all.
   Do not import or reference anything from that project's code directly —
   it's a different repo with different conventions (implicit Gprims in
   places, different scope names). Learn the *technique*, reimplement it
   here using our own established helpers and §2.1-§2.5 conventions.

## Before you start

```
git checkout main
git pull --ff-only
git checkout -b feat/phase3-vehicle-roster
```

(If this branch already exists locally from the superseded attempt, make
sure `pipeline/vehicle_utils.py` and `pipeline/build_vehicles.py` are gone
before starting — this prompt rewrites both from scratch.)

## Task 1 — Generic geometry helpers (`pipeline/usd_utils.py`)

These are general-purpose primitive authoring helpers, not vehicle-specific
— they belong alongside `make_box_mesh`/`make_cylinder_mesh`, since other
future phases (Terrain's Ridge Line cliff edges, a Checkpoint booth roof)
could plausibly want them too.

- **`make_profile_extrusion(stage, path, profile_points, half_width)`** — a
  generic 2D polygon (a list of `Gf.Vec2f`, walked in one winding direction
  in the Y-Z-equivalent plane) extruded across a width axis, exactly the
  technique in the tank's `chassis.py` hull: two end caps (wound oppositely
  so both face outward) plus one side quad per profile edge connecting the
  two extruded copies. Must work for **any** profile point list the caller
  passes — don't hardcode a specific shape; the Mule/Goat prompts will each
  pass their own hood/cab profile.
- **`make_frustum_mesh(stage, path, bottom_radius, top_radius, height,
  axis="Y", sides=16)`** — generalizes `make_cylinder_mesh` to allow
  different top/bottom radii (a tapered cylinder), per the tank turret
  technique. Refactor `make_cylinder_mesh` to call this with
  `bottom_radius == top_radius == radius` rather than keeping two separate
  ring-generation implementations — confirm the refactor doesn't change
  `make_cylinder_mesh`'s existing behavior (Phase 0/1/2 callers must be
  unaffected).
- Both must produce correct flat per-face normals and valid UVs, consistent
  with every other mesh helper in this file (reuse the existing normal/UV
  authoring pattern, don't reinvent it).

## Task 2 — Referenceable wheel-corner sub-assembly generator

**Design constraint, load-bearing:** author the wheel-corner asset
**mirror-symmetric in its own local space** (tire/rim are already
rotationally symmetric cylinders/frustums; keep any wheel-arch flare
geometry symmetric too — no asymmetric detail like a valve stem on one
particular side). This means the *same* corner asset can be referenced at
both `+X` and `-X` positions via a **plain translate override, no rotation,
no mirroring** — sidestepping the winding/normal-flip pitfall entirely
rather than working around it.

Write a generator (in a new `pipeline/vehicle_utils.py`) that authors **one
standalone, exportable `.usda`** per corner type, parametrized by tire
radius/width, wheel-arch size, suspension-strut travel length, and a
steerable flag:

- **Front corner** (steerable): `_Steer` pivot (rotateY) parenting `_Spin`
  (rotateX) parenting the tire+rim meshes, matching Phase 1's validated
  two-level chain.
- **Rear corner** (fixed): a bare `_Spin` pivot only.
- Both include the wheel-arch flare and suspension strut as part of the
  same corner asset (Geometry scope), since they're positioned relative to
  the wheel, not the chassis.
- Export each corner asset as its own `.usdz`/`.glb` pair too (so it's
  independently viewable/testable — that's the actual point of building it
  as a real sub-asset rather than an inline function call) using the
  `asset_output_paths` convention, under category `"Vehicle"`.

This generator function itself is the "shareable, customizable" part: Phase
3b calls it with the Mule's road-tire parameters to produce
`VehicleMuleFrontCorner`/`VehicleMuleRearCorner`; Phase 3c calls the *same*
function with the Goat's off-road-tire/long-travel parameters to produce
its own corner assets. Don't parametrize anything you don't have a concrete
second caller for yet, but do keep tire style, radius, width, arch size, and
travel length as real parameters (not hardcoded), since Phase 3c needs all
of them to differ.

## Task 3 — Detail/greeble kit (`pipeline/vehicle_utils.py`)

Parametrized, reusable functions — headlight (housing + lens, two parts,
matching the tank's pattern), mirror, bumper, and whatever else reads as
"more than a bare box" once actually rendered. Learn from the specific
mistake in the superseded attempt's follow-up prototyping (recorded in the
Review Log): a window/glass panel sized as a fraction of its parent
volume's full height/length reads as a solid dark wall slab, not a window —
size these against real proportions (a vehicle window band is a small
fraction of cab height, not most of it), and **render a check before
trusting a size**, not just eyeball the numbers.

## Task 4 — Hull/cab composition using profile extrusion

Not a single rigid function — each vehicle's body differs — but build at
least one concrete, reusable helper on top of Task 1's primitive, e.g. a
sloped hood/windshield wedge builder that takes a profile point list and a
half-width and returns the extruded mesh, positioned and colored by the
caller. Phase 3b and 3c will each supply their own profile points (a van's
hood slope differs from a pickup's).

## Task 5 — Validation harness (required; this is how you catch a Task-3-style mistake before it reaches review)

Build a **throwaway** test script (not a production build script — this
phase ships no vehicle) that:

1. Generates one front-corner and one rear-corner asset with placeholder
   parameters, references both into a tiny test stage at mirrored `±X`
   positions (proving the symmetric-reference design works, no mirroring
   needed).
2. Builds one test hull section via `make_profile_extrusion` with a simple
   sloped wedge profile (proves the extrusion helper produces correct,
   outward-facing geometry — not inside-out).
3. Builds one test frustum via `make_frustum_mesh` with `top_radius !=
   bottom_radius` (proves the taper works).
4. Runs `usdchecker` on all of it.
5. **Renders it via headless Blender and actually looks at the image**
   (the same pattern this conversation used manually to catch the superseded
   attempt's problems — don't skip straight to "usdchecker passed, done").
   Save the render(s) under `pipeline/.build/_review/` (gitignored) and
   report the exact path(s) so they can be opened afterward.

Delete this throwaway script once it's served its purpose, same rule as
every prior phase's validation scripts — report whether you did.

## Acceptance criteria

- `make_profile_extrusion` and `make_frustum_mesh` exist in `usd_utils.py`,
  produce valid meshes (`usdchecker` clean, correct outward normals
  confirmed by the Task 5 render, not just schema validity).
- `make_cylinder_mesh` refactored to use `make_frustum_mesh` internally with
  no behavior change for existing callers.
- Wheel-corner generator produces a front and rear corner asset, each
  independently exportable and `usdchecker`-clean, with the correct
  `_Steer`→`_Spin` / bare-`_Spin` pivot chains.
- The mirrored-reference test (Task 5.1) renders correctly from both sides
  with no visible winding/normal artifacts.
- At least one detail/greeble function exists and, per Task 3, has been
  render-checked at realistic proportions, not just eyeballed.
- `npm run check` still passes (no runtime code should need touching this
  phase, but confirm).
- No throwaway validation code committed.

## What to report back

- Every new/changed function's signature and where it lives.
- The Task 5 render image path(s) — this is the most important thing to
  hand back, since it's what makes this phase's result actually reviewable
  without me re-deriving it from code alone.
- Confirmation the wheel-corner symmetric-reference design works as
  intended (no mirroring needed, no normal-flip artifacts).
- Anything about the kit's shape that felt awkward or under-specified,
  especially anything Phase 3b (the Mule) will need that isn't here yet —
  better to flag a gap now than discover it mid-assembly.
- Any deviation from this prompt and why.

Do not build a full vehicle (Mule or otherwise) — that's Phase 3b, a
separate prompt. Stop after this prompt's acceptance criteria are met and
report back.
