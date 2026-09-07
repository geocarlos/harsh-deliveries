# Prompt — Phase 3b: The Mule, Assembled From the Shared Kit

Paste this whole file as your first message in a **new** Claude Code session
opened at the repo root. That session has no memory of any prior session —
everything it needs is either in this file or in files it points to.

This is the second of three prompts making up roadmap Phase 3 (revised) —
see `docs/prompts/INDEX.md`. Phase 3a (merged into this branch already)
built a shared, customizable vehicle kit: profile-extrusion/frustum geometry
helpers (`usd_utils.py`) and a referenceable, mirror-symmetric wheel-corner
generator plus a detail kit (`vehicle_utils.py`). This prompt assembles the
**Mule** from that kit — the first real vehicle, and the reason the kit was
built the way it was. Phase 3c (a separate prompt, after this one is
reviewed) assembles the **Goat** from the *same* kit with different
parameters, as the explicit proof the kit generalizes. All three share
`feat/phase3-vehicle-roster` — no new branch needed, just continue on it.

**Same instruction as Phase 3a: trade speed for realism and detail. Do not
rush this.**

## Context to read first

1. `CLAUDE.md` (repo root) — already auto-loaded.
2. `docs/architecture/asset-roadmap.md` — §1.1 (Vehicles, the Mule's traits:
   Cargo Care+, Capacity+ / Terrain Traction−), §2.1-§2.5 (scope skeleton,
   rig/hardpoint/collision conventions).
3. `docs/game-design/02-character-and-vehicle-design.md` §4.1 — the Mule's
   actual design brief.
4. `docs/prompts/INDEX.md`'s Review Log — read the Phase 3a-revised entry
   and the rejected-original-Phase-3a entry before it. The second entry's
   account of *why* the first Mule attempt failed (flat-slab chassis,
   floating shoebox cargo box, no hood/cab/windshield distinction) and what
   the v2-v4 prototyping found actually fixed it (real vehicle anatomy —
   hood, cab, greenhouse, wheel arches, bumpers, proportionate windows) is
   directly relevant here — don't repeat that mistake by falling back to
   "one box for chassis, one box for cargo."
5. `pipeline/vehicle_utils.py` and `pipeline/usd_utils.py` — read
   `build_wheel_corner`, `build_headlight`, `build_mirror`, `build_bumper`,
   `build_window_band`, `build_hull_section`, `make_profile_extrusion`, and
   `make_frustum_mesh` in full; these are what you're assembling from.
6. `pipeline/cargo_utils.py` — `PALLET_LENGTH`/`PALLET_WIDTH`/
   `TIE_DOWN_INSET`. The cargo box's `TieDown_01..04` **must** reuse these
   exact constants (import them), not new numbers — this is the actual
   point of the shared hardpoint convention (§1.1/§1.7): any cargo container
   mounts any compatible bed.
7. `pipeline/.build/_review/mule_v4_prototype.usda` (and its render,
   `mule_v4_prototype.png`) — a **prior, discarded** prototype (built from
   plain boxes, before the kit existed) that got the Mule's *proportions*
   right (wheel positions, hood/cab/cargo-box lengths, ride height) even
   though its *construction technique* is exactly what this phase is
   replacing. Reuse the validated numbers as a starting point; don't reuse
   its box-only construction.

## Before you start

```
git status   # confirm you're on feat/phase3-vehicle-roster with a clean tree
```

No new branch — Phase 3a's commit is already on `feat/phase3-vehicle-roster`.

## Task 1 — Extend the kit: door hinge + cargo latch

`vehicle_utils.py` doesn't have these yet (Phase 3a's validation harness
didn't need them). Add, following the same pattern as its existing
functions (parametrized, reusable — Bastion's rear doors, Goat's tailgate,
Needle's trunk, and the Wasp's hauler lid will all call these later):

- `add_door_hinge(stage, rig_scope, name, hinge_position, door_size, ...)` —
  a `_Hinge` pivot (rotateY) + door panel mesh, hung from its hinge edge
  (mesh offset by half its swing width from the pivot, so the door's far
  edge swings, not its hinge edge).
- `add_cargo_latch(stage, rig_scope, name, latch_position, ...)` — a
  `_Latch` pivot (rotateX) + small latch mesh. **Use `_Latch`, not
  `_Hinge`** — see Phase 3a-original's Context item 4 (now in the
  superseded prompt file) for why the two are distinct suffixes, not
  interchangeable.

## Task 2 — Build the Mule's two wheel corners

Call `vehicle_utils.build_wheel_corner` twice — once `steerable=True` (front,
road tire), once `steerable=False` (rear, road tire) — with the Mule's own
tire radius/width (the v4 prototype's `wheel_radius=0.36, wheel_width=0.22`
are a reasonable starting point). This produces two standalone `.usda`
files under `pipeline/.build/`. Confirm both export cleanly before moving on
(same `usdchecker` + `usdtree` check Phase 3a's review already did on
generic test corners — now with the Mule's actual parameters).

## Task 3 — Assemble the hull

Use `make_profile_extrusion` (via `build_hull_section`) for the
**hood-into-windshield panel** — a single continuous sloped surface, not a
flat hood box glued to a separate flat glass plate (the v2-v4 prototypes'
remaining weakness). A concrete starting profile, adapted from the
reference tank's own hull-profile pattern (walk the same rotational
order — bottom-rear, bottom-front, top-front, top-rear, close back to
bottom-rear — just with a van's proportions instead of a tank's glacis):

```
profile = [
    (cab_front_z,    deck_y),       # bottom-rear (meets the cab's base)
    (hood_front_z,   deck_y),       # bottom-front (front bumper line)
    (hood_front_z,   hood_top_y),   # hood's flat top, at the front
    (windshield_base_z, hood_top_y),# where the hood meets the windshield base
    (cab_front_z,    roof_y),       # top of windshield, meets the roofline
]
```

(Points are `(z, y)` — depth, height — per `make_profile_extrusion`'s
convention; this closes back to the first point automatically, forming the
cab-front face as the closing edge.) Tune the actual numbers to the Mule's
proportions; **render it and look before trusting it** — Phase 3a's
validation render already proved this helper produces correct outward-facing
geometry for a wedge shape, so if yours looks inside-out or degenerate, the
profile point *order* or a self-intersecting shape is the likely cause, not
the helper.

Cab body, greenhouse, and cargo box can stay boxes (`make_box_mesh`) — those
genuinely are box-shaped in reality; it's the hood/windshield transition
that most needed the sloped surface. Use `build_window_band` for the cab's
side glass (sized as an absolute band height, not a fraction of cab
height — Task 3's own docstring explains why). Cargo box: reuse
`cargo_utils`' pallet-footprint constants for `TieDown_01..04` exactly as
Context item 6 requires.

## Task 4 — Reference the wheel corners into the assembly (this is the actual point of Phase 3a's design)

Reference each corner asset **twice** (front corner at both `FL`/`FR`
positions, rear corner at both `RL`/`RR`) via a plain **translate-only**
override — no rotation, no mirroring, per Phase 3a's mirror-symmetric
design. Attach the four reference prims as children of the Mule's own `Rig`
scope (e.g. `/Vehicle_Mule/Rig/WheelCorner_FL`), **not** as a new top-level
scope — the roadmap's §4 hierarchy gate requires the Mule's own *top-level*
structure to match the exact five-scope skeleton, and nesting the reference
under `Rig` preserves that even though the referenced asset brings its own
nested `Geometry`/`Rig`/`Hardpoints`/`Collision`/`Materials` subtree one
level down. This is a deliberate call, not an oversight — confirm the final
`usdtree` still shows exactly `Geometry`/`Rig`/`Hardpoints`/`Collision`/
`Materials` at `/Vehicle_Mule`'s own top level.

**Expect, and don't "fix," this:** because all four references point at
only two distinct source files, the composed scene has **multiple nodes
sharing the same leaf name** (`Wheel_Spin` appears four times, `Wheel_Steer`
twice) — nested at different parent paths (`.../WheelCorner_FL/Rig/...` vs
`.../WheelCorner_FR/Rig/...`), so no path collision, but also no per-corner
disambiguation baked into the leaf name itself. This is intentional and
matches the roadmap's own stated Babylon lookup strategy (§2.2: find *every*
node ending in a suffix and drive it identically) — the suffix convention
was never meant to distinguish individual wheels, only to find all of them.

## Task 5 — Details, hardpoints, collision

- Headlights, mirrors, front/rear bumpers via `vehicle_utils`' existing
  functions.
- Rear door(s) via Task 1's `add_door_hinge`; cargo latch via Task 1's
  `add_cargo_latch`.
- `Collision/Hull_*` — at minimum a chassis hull and a cargo-box hull
  (`make_box_mesh`, §2.5). Non-negotiable per the roadmap (Cargo Integrity
  reads off vehicle physics signals).
- `Hardpoints/DriverSeat` + `Hardpoints/ExitPoint` at sensible positions.
- Export via `asset_output_paths(MODELS_DIR, "Vehicle", "Mule")`.

## Task 6 — Babylon validation

Using the `run` skill (or `npm run dev` + a browser): load the Mule's
`.glb`, confirm zero console errors. Then, temporarily (same throwaway
pattern as Phase 1/the original Phase 3a): drive the wheels.

**Use a lookup that finds every matching node, not just the first** (e.g.
`scene.transformNodes.filter(n => n.name.endsWith('_Spin'))`, not `.find`)
— per Task 4, there are now four `_Spin` nodes and two `_Steer` nodes, and
the point of this validation is confirming all of them move correctly, not
just one. Confirm:
- All four `_Spin` nodes roll about their own lateral axis at their own
  position (not the chassis origin).
- Both `_Steer` nodes turn about a vertical axis at their own wheel
  position.

Remove the snippet from `main.ts` before finishing.

## Acceptance criteria

- Clean `.usdz`/`.glb` export; `usdchecker` clean.
- `usdtree` shows the Mule's own top-level scopes as exactly `Geometry`/
  `Rig`/`Hardpoints`/`Collision`/`Materials` (Task 4).
- All four wheel-corner references resolve correctly (no dangling
  reference, confirmed by opening the flattened output and checking the
  referenced geometry is actually present under each `WheelCorner_*` path).
- `Collision/Hull_*` present; `DriverSeat`/`ExitPoint` present.
- `TieDown_01..04` on the cargo box numerically match `cargo_utils`'
  pallet-footprint constants (not just visually close).
- Babylon test (Task 6) passes for all four wheels.
- **A render you actually looked at**, saved under `pipeline/.build/_review/`
  — this is now a standing requirement for every vehicle-kit phase, not
  optional. Compare it honestly against `mule_v4_prototype.png`: is it at
  least as good? If something regressed, say so in your report rather than
  presenting it as done.
- `npm run check` passes; no throwaway runtime/validation code committed.

## What to report back

- The render path(s), and your own honest comparison against
  `mule_v4_prototype.png`.
- Confirmation of the reference/nesting structure (Task 4) and that the
  Babylon multi-node lookup (Task 6) found and correctly drove all six
  wheel pivots.
- The hood/windshield profile points you landed on, and whether the
  suggested starting profile in Task 3 needed adjustment.
- New `add_door_hinge`/`add_cargo_latch` signatures (Task 1) — Phase 3c and
  beyond will call these too.
- Any deviation from this prompt, and anything Phase 3c (the Goat) should
  know before reusing this same kit with different parameters.

Do not build the Goat — that's Phase 3c, a separate prompt. Stop after this
phase's acceptance criteria are met and report back.

---

## Round 2 (2026-09-07) — fix the cab/cargo-box junction

Paste this section (plus the header above it for context) into a **new**
Claude Code session, same repo, same branch (`feat/phase3-vehicle-roster`,
already has the Round-1 work uncommitted in the working tree — confirm with
`git status` before starting, don't re-run Round 1's tasks).

**What's wrong:** reviewed by rendering the actual result (Blender, multiple
angles) and taking an in-engine Babylon screenshot, not just reading code.
Everything passed except one visible flaw: a distracting ledge/shoulder
where the cab's `CabGreenhouse` meets `CargoBox`. Verified this is **not**
a roofline height mismatch — direct extent query confirms both tops sit at
exactly `Y=2.35`, genuinely flush — it's a **width** mismatch:
`CabLower` half-width `0.85` → `CabGreenhouse` narrows to `0.78` →
`CargoBox` widens back out to `0.93`, wider than either. The cargo box's
front-top corners visibly poke out past the greenhouse right at the seam
the build script's own comments say was meant to read as "one continuous
panel, no separate bridging trim." It doesn't — if anything it reads worse
there than the discarded `mule_v4_prototype.png`'s simpler stepped
roof-bridge, which spread the transition across three smaller steps instead
of concentrating one large one at a mismatched-width junction.

**Fix it** by removing the width mismatch at that specific junction — the
simplest approach is probably making `CabGreenhouse`'s width match
`CargoBox`'s (`0.93`) rather than narrowing to `0.78`, so the box continues
the greenhouse's width without a jump; a tapered transition (narrower at the
windshield, widening smoothly back to the cargo box's width) is also
reasonable if a flat match reads too slab-sided, but must actually be
rendered and checked, not just reasoned about. `CabLower`'s own width
relative to the greenhouse is a separate, smaller step that read fine in
the review render — don't feel obligated to touch it unless fixing the
greenhouse/cargo-box seam interacts with it.

**Re-verify, don't just assume the fix worked:**
- Rebuild, re-render (reuse the same render approach — multiple angles,
  actually look at the image) and confirm the ledge is gone.
- Re-run the Babylon load and confirm nothing else regressed.
- `usdchecker` clean, `npm run check` passes.

## Round 2, second fix — the wheel corner is unreadable in isolation

Found by the user viewing `vehicle_mulefrontcorner.usda` (or the
generic Phase 3a test corners, same underlying code) directly in a
standalone USD viewer: "without the name, I'd have no idea what I'm looking
at." This is not a lighting complaint — confirmed by direct geometry query,
two real bugs in `vehicle_utils.py`'s wheel-corner generator:

1. **The `Rim` mesh is entirely nested inside the `Tire` mesh's solid
   volume — invisible from every camera angle.** Confirmed via
   `UsdGeom.Mesh.GetExtentAttr()`: `Tire` spans local X `[-0.11, 0.11]`
   (radius 0.36), `Rim` spans X `[-0.077, 0.077]` (radius 0.22) — a smaller
   solid cylinder centered fully inside a bigger one, on every axis. Since
   neither has an actual hole/opening (both are solid capped cylinders),
   the rim contributes zero visible surface. **Fix:** offset the rim's
   translate along the tire's own axis so it sits flush with (or slightly
   proud of) the tire's *outboard* face (the face pointing away from the
   vehicle's centerline — i.e. the direction `position[0]`'s sign already
   indicates elsewhere in this file), not centered inside it. The rim is
   supposed to be the single most visually distinctive "this is a wheel"
   cue — it doing nothing at all is the core of why this reads as
   unrecognizable.
2. **The wheel-arch flare's default `arch_span_degrees=220` wraps most of
   the wheel's circumference**, not the top arch a real fender covers —
   from most angles it reads as a shell encasing the whole wheel rather
   than a flare over the top of a clearly visible tire. Reduce the default
   substantially (something in the 140-160° range is a reasonable starting
   point) and **render a standalone wheel-corner in isolation** (exactly
   the scenario that surfaced this — not just assembled into the full
   Mule) to confirm it now reads as "a wheel with a fender," unaided by
   context or a filename label.

Both fixes are in the same shared kit file every vehicle (Goat, Needle,
Bastion, Wasp too) will call — worth getting right now rather than letting
it propagate.

**Re-verify:** render `vehicle_mulefrontcorner.usda` (or a fresh standalone
test corner) alone, from a few angles, with no other vehicle geometry in
frame — the actual bar to clear is "readable as a wheel with no label,"
per the user's own framing of the problem.

**Report back:** the new render path(s), the rim's new offset value, and
the arch span you landed on — plus confirmation the full Mule assembly
(Round 1 + Round 2's first fix) still looks correct with the updated wheel
corners referenced in.
