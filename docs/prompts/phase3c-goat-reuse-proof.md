# Prompt — Phase 3c: The Goat, Proving the Kit Actually Generalizes

Paste this whole file as your first message in a **new** Claude Code session
opened at the repo root. That session has no memory of any prior session —
everything it needs is either in this file or in files it points to.

This is the third of three prompts making up roadmap Phase 3 (revised) — see
`docs/prompts/INDEX.md`. Phase 3a built a shared, customizable vehicle kit;
Phase 3b proved it by assembling the Mule. This prompt assembles the **Goat**
(off-road pickup) from the *same* kit, with different parameters — the
explicit point of this phase is proving the kit generalizes to a genuinely
different vehicle, not just re-parametrizing the Mule. Continue on
`feat/phase3-vehicle-roster` — no new branch.

**Same instruction as 3a/3b: trade speed for realism and detail.**

## Context to read first

1. `CLAUDE.md` (repo root) — already auto-loaded.
2. `docs/architecture/asset-roadmap.md` — §1.1 (the Goat's traits: Traction+,
   Durability+ / Profile−; open bed, lifted suspension, knobby off-road
   tires, roll-bar/brush-guard props — explicitly distinct from the Mule).
3. `docs/game-design/02-character-and-vehicle-design.md` §4.2 — the Goat's
   actual design brief.
4. `docs/prompts/INDEX.md`'s Review Log — read the full Phase 3b entry
   (both Round 2 fixes) so you understand what "render and actually look"
   caught last time and don't repeat those specific mistakes (oversized
   window-as-wall-slab, geometry nested invisibly inside other geometry,
   width mismatches at panel seams).
5. `pipeline/vehicle_utils.py`, `pipeline/build_vehicles.py`,
   `pipeline/usd_utils.py` — read in full. `build_vehicles.py` is the
   closest precedent for this file's `build_goat()` (same file, new
   function — extend `VEHICLE_VARIANTS`-equivalent... actually this file
   currently only calls `build_mule()` directly from
   `build_vehicle_roster()`; add `build_goat()` there too, following the
   same per-vehicle-function pattern).
6. `pipeline/cargo_utils.py` — the pallet/tie-down constants the Goat's open
   bed must reuse exactly, same as the Mule's enclosed box did.

## Before you start

```
git status   # confirm you're on feat/phase3-vehicle-roster, Phase 3b's
             # commit already present, working tree clean
```

## Task 1 — Fix the suspension strut (kit-level; affects the Mule too)

**Root cause, confirmed by direct geometry math, not just the visual
complaint that prompted this:** `build_wheel_corner`'s strut spans local Y
`[tire_radius, tire_radius + strut_length]` before the corner is referenced;
referencing adds the wheel-center world height (`tire_radius` again, since
wheels are placed at `y=tire_radius` so they touch the ground) on top. For
the Mule (`tire_radius=0.36`, default `strut_length=0.35`, never overridden
by `build_mule()`), that puts the strut's top at world `Y≈1.07` — *above*
the chassis rocker panel's own bottom edge (`≈0.56`) and past its top
(`0.92`), i.e. the strut clips up through the body by a wide margin, floating
disconnected rather than terminating against anything. This is why it reads
as a bare pole poking through the roofline.

Fix, in two parts:

- **`vehicle_utils.py`:** add a small mount-plate cap (a thin disc or box) at
  the strut's top end, so it visually terminates against something instead
  of ending in bare air. A slight inward tilt (a few degrees) is a nice
  MacPherson-strut touch if it's cheap to add — optional, don't force it if
  it complicates the mirror-symmetric corner design from Phase 3a.
  Steering-linked strut rotation (a real MacPherson strut is part of the
  steering knuckle, so it'd rotate with `_Steer`) is explicitly **not**
  required this phase — only add it if it turns out to be nearly free
  given the existing pivot structure; don't restructure the corner for it.
- **Every caller must compute `strut_length` from its own vehicle's actual
  wheel-well depth** (the gap between the wheel's top and wherever that
  vehicle's own body underside actually sits), not rely on the generic
  default — **verify by rendering**, the same way every other geometry
  claim in this project has been verified, not by trusting the arithmetic
  alone (the rocker-panel overlap math above has enough moving parts that
  eyeballing the render is the real check). This means going back and
  giving `build_mule()`'s two `build_wheel_corner` calls an explicit,
  correct `strut_length` too — **the Mule's strut is wrong today and this
  is the natural point to fix it**, since it's the same shared function.
  Re-render the Mule after this change and confirm the strut now terminates
  cleanly at the body, not through it.

## Task 2 — Generalize the door-hinge kit for a tailgate

`add_door_hinge` currently only supports a vertical hinge line (rotateY,
side-swinging barn doors — correct for the Mule's rear doors). A pickup
tailgate hinges at the **bottom** edge and swings **down** (rotateX, a
horizontal hinge line) — the roadmap's own §1.1 explicitly names "tailgate
(Goat)" as one of this kit's intended use cases, so this is expected
generalization, not scope creep. Add a `hinge_axis` parameter (`"X"` or
`"Y"`, defaulting to `"Y"` so the Mule's existing calls are unaffected) that
picks the pivot's rotate axis and adjusts the panel-offset math accordingly
(a bottom-hinged tailgate offsets along Y from the pivot, not X like a
side-hinged door — reuse the existing sign-based offset logic, generalized
to whichever axis is actually swinging).

## Task 3 — New detail kit pieces: roll bar, brush guard

Both named explicitly in the Goat's design brief. Keep them simple,
consistent with every other detail piece in this file:

- **Roll bar**: two vertical posts + one horizontal bar connecting their
  tops (a simple "goalpost" shape via `make_cylinder_mesh`, not a bent/
  curved tube) arching over the open bed.
- **Brush guard**: a small tubular frame across the front bumper area,
  same construction philosophy (a few straight cylinder/box segments, not
  a curved welded tube).

Add these as new `vehicle_utils.py` functions (`build_roll_bar`,
`build_brush_guard`) — reusable for other vehicles later (Bastion's
armored front could plausibly want a brush-guard-style piece too), not
one-off code in `build_vehicles.py`.

## Task 4 — Assemble the Goat

In `pipeline/build_vehicles.py`, add `build_goat()` (and call it from
`build_vehicle_roster()` alongside `build_mule()`):

- **Reuse, don't fork.** The whole point of this phase is calling the exact
  same `vehicle_utils` functions the Mule uses — `build_wheel_corner`,
  `build_hull_section`, `build_headlight`, `build_mirror`, `build_bumper`,
  `build_window_band`, `add_door_hinge`, `add_cargo_latch` (if the tailgate
  needs a latch too) — with Goat-specific parameters, not copies of them.
  If you find yourself wanting to copy-paste a function and change a few
  lines, that's a sign it needs one more parameter, not a fork.
- **Wheel corners**: off-road tire parameters (larger radius/width than the
  Mule's road tires; differentiate the "knobby" look through proportions
  and the existing `rubber` preset — actual tread-block geometry is not
  required, that's more detail than this scope needs) and the Task 1
  corrected, vehicle-specific `strut_length` reflecting the Goat's *lifted*
  stance (longer travel than the Mule — this is a real, visible proportion
  difference the roadmap calls for, not just a number).
- **Hull**: hood-into-windshield via `build_hull_section` again, but with
  the Goat's own profile points — a pickup's proportions differ from a
  van's (shorter cab, no tall box body). Cab body/greenhouse stay boxes,
  same reasoning as the Mule.
- **Open bed**, not an enclosed box: a shallow floor pan + low side rails
  (not a full box), with `TieDown_01..04` on the bed floor via
  `cargo_utils`' constants, exactly like the Mule's tie-downs (same
  footprint convention, different bed archetype).
- **Tailgate** via Task 2's generalized `add_door_hinge(..., hinge_axis="X")`
  at the bed's rear edge.
- Roll bar (Task 3) over the bed; brush guard (Task 3) at the front.
- Headlights, mirrors, front bumper via existing functions.
- `Collision/Hull_*` (chassis + bed, at minimum), `Hardpoints/DriverSeat` +
  `ExitPoint`.
- Export via `asset_output_paths(MODELS_DIR, "Vehicle", "Goat")`.

## Task 5 — Render and check (both vehicles)

- Standalone Goat wheel corner in isolation, same bar as Phase 3b's fix:
  readable as "a wheel with a fender" with no label.
  render the full Goat from a few angles.
- **Re-render the Mule too** — Task 1's kit change affects it, and this is
  the regression check for that. Confirm the strut now terminates at the
  body and nothing else changed for the worse.
- Babylon load for the Goat's `.glb`: zero console errors, multi-node
  suffix lookup (`.filter`, not `.find`, per Phase 3b's own lesson) finds
  and correctly drives its `_Steer`/`_Spin` nodes.

Save renders under `pipeline/.build/_review/` and report the paths.

## Acceptance criteria

- `usdchecker` clean on the Goat, its wheel corners, and the re-rendered
  Mule.
- **Reuse confirmed structurally, not just by claim**: grep/review
  `build_goat()` and confirm it imports and calls the same `vehicle_utils`
  functions as `build_mule()` — no forked/duplicated geometry-authoring
  code for anything both vehicles share.
- Suspension strut (Task 1) terminates cleanly against the body on *both*
  vehicles, confirmed by render.
- Tailgate (Task 2) opens on a horizontal hinge, distinct from the Mule's
  vertical barn-door hinge, using the same underlying function.
- Open bed's `TieDown_01..04` numerically match `cargo_utils`' constants.
- Roll bar and brush guard present and read as intentional details, not
  boxes floating in space (render-checked).
- Goat visually distinguishable from the Mule at a glance (different
  silhouette: open bed vs. enclosed box, shorter cab, lifted stance, knobby
  wider tires) — a soft check, but a real one per the roadmap's own design
  intent that players recognize vehicles by silhouette.
- Babylon test passes for the Goat; Mule regression check passes.
- `npm run check` passes; no throwaway runtime/validation code committed.

## What to report back

- Confirmation of Task 1's fix on both vehicles (render paths, before/after
  if easy to show for the Mule).
- The `hinge_axis` signature change and confirmation the Mule's existing
  `add_door_hinge` calls still work unmodified.
- New `build_roll_bar`/`build_brush_guard` signatures.
- The Goat's tire/strut/hull parameters, for comparison against whatever
  Needle/Bastion end up needing later.
- Any deviation from this prompt, and anything that still felt awkward or
  under-generalized about the kit — this is the last phase before deciding
  how Needle, Bastion, and the Wasp get scoped, so surface anything here.

Stop after this phase's acceptance criteria are met and report back — don't
start Needle, Bastion, or the Wasp; those get their own prompts, planned
after this one's reviewed.
