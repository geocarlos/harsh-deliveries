# Phased Asset Architecture & Implementation Roadmap

**Status:** Draft v1 — architectural design only, no generator code written against it yet. Derived from `docs/game-design/` Modules 1–4 (Version 0, approved) plus the existing pipeline scaffold in `pipeline/` (`usd_utils.py`, `export_utils.py`, `build_assets.py`).

**Scope note (read first, updated):** This roadmap's asset-*production* focus for Phases 0–5 is **Vehicles, Cargo, Terrain/Geography, Hazards, and Props** — the five categories the brief named. **Runner (character) models are intentionally not full-detail production content in this pass**, but they are not out-of-architecture either: the producer has flagged on-foot gameplay (sneaking away from a parked vehicle, commandeering a second vehicle to run interference for the cargo vehicle) as a real future direction, not a hypothetical — so runners get a reserved category, naming convention, and vehicle-side mount/dismount hardpoints *now* (§1.6, §2.3), populated today with placeholder geometry (a capsule or billboard card, not a rigged humanoid), so that swapping in real character models later is a content change, not an architecture change. Full humanoid rigging (skeleton/skinning through the Blender glTF path, walk/sneak animation) stays explicitly deferred — see the "Phase 6 (Deferred)" note at the end of §3 — but nothing in Phases 0–5 should make that later work harder than it has to be.

---

## 1. Asset Inventory & Modularity Breakdown

### 1.1 Vehicles (5 roster entries, Module 2 §4)

| Asset | Headline traits (Module 2) | Distinguishing geometry needs |
|---|---|---|
| **The Mule** (cargo van) | Cargo Care+, Capacity+ / Traction− | Large enclosed cargo box, rear/side latching doors, road tires |
| **The Goat** (off-road pickup) | Traction+, Durability+ / Profile− | Open bed, lifted suspension travel, knobby off-road tires, roll-bar/brush-guard props |
| **The Needle** (unmarked sedan) | Profile+, road speed+ / Capacity− | Small trunk, low-profile road tires, no exterior cargo tells |
| **The Bastion** (armored transport) | Durability+, Capacity+ / Cargo Care−, Profile− | Armor plating shell, reinforced/heavy suspension (visually stiff), enclosed armored box |
| **The Wasp** (cargo motorcycle + sidecar) | Traction+ (narrow lines), Profile+ / Durability−, Capacity− | Two-wheel bike geometry, sidecar hauler as a distinct attached sub-assembly |

**Shared vehicle sub-components** (built once in Phase 3, parameterized per vehicle):
- **Chassis frame/rail kit** — parametric box-rail frame, scaled per vehicle class (van/pickup/sedan/armored truck/bike frame).
- **Wheel assembly kit** — road tire, off-road (knobby) tire, motorcycle tire — each riggable as steerable-front / fixed-rear (§2.2).
- **Suspension mount kit** — visual travel range differs (Goat = long travel, Bastion = stiff/short, Needle = low stance).
- **Cargo bed/box kit** — open bed (Goat), enclosed box (Mule), armored box (Bastion), trunk (Needle), sidecar hauler (Wasp) — all built from the same **Cargo Container kit** hardpoint conventions in §1.2 so any bed type can mount any compatible cargo container.
- **Door/hatch hinge kit** — rear doors (Mule, Bastion), tailgate (Goat), trunk lid (Needle), hauler lid (Wasp).
- **Cargo latch/lock kit** — the "latching cargo bay locks" CLAUDE.md calls out explicitly; a small hinged/sliding latch prim reused wherever a cargo bay closes.
- **Lighting & marker prop kit** — headlights, taillights, livery/decal attach points (flat quads or shallow boxes with a livery-variant material, not full texture painting).

### 1.2 Cargo (Module 1 §6.1, Module 4 §5 sample missions)

| Cargo profile (from sample missions) | Fragility | Legality | Container archetype |
|---|---|---|---|
| Canned goods | Low | Legal | Wood crate |
| Glassware | High | Legal | Glass-panel case |
| Machine parts | Medium | Legal | Metal parts crate |
| Undeclared/illegal cargo | Low (physical) | Illegal | Sealed unmarked container |
| Volatile chemical drums | High | Illegal | Steel drum (banded) |

**Shared cargo sub-components:**
- **Pallet base** — common footprint every container variant sits on, carrying the tie-down hardpoints.
- **Tie-down point kit** — non-rendering marker Xforms at standardized pallet corners (see §2.3), shared by every cargo container *and* every vehicle bed, so any container can visually "belt into" any compatible bed.
- **Container shell kit** — crate, drum, case, sealed-box variants, differentiated by silhouette + material only (wood/matte, steel/metallic, glass/translucent-preview, unmarked/flat) — not by unique rigging, since cargo doesn't animate on its own.
- **Multi-unit stacking** — authored once via `UsdGeom.PointInstancer` for fast iteration, then **baked** to explicit prims before export per `export_utils.bake_all_point_instancers()` (instancing isn't reliably portable — see `usd-dcc-export` skill).

### 1.3 Terrain / Geography (Module 4 §3.1)

| Hazard | Geometry need |
|---|---|
| **Washout** | Standard road tile + a distinct traction-flag material zone (mud/ice/gravel patch) |
| **Ridge Line** | Narrow road tile, no guardrail, cliff-edge drop-off geo, vehicle-profile-gated width |
| **Bog Crossing** | Wide, shallow mud-pool tile, flat but visually distinct from Washout |
| **Blind Switchback** | Sharp-turn tile + blocking geometry (rock wall / vegetation) that occludes sightline into the fork |

**Shared terrain sub-components:**
- **Road tile kit** — straight, curve, junction, fork (Blind Switchback base), each authored on a common **snap convention**: tile origin at one edge, fixed tile width/length unit, so tiles chain by translation alone (no per-tile custom alignment math at level-assembly time).
- **Regional biome dressing kits** — neutral, mountain corridor (Highland/Iveta's region), swamp, dockside/urban — rock/vegetation/dockside prop sets layered onto the generic tile kit rather than separate geometry per region.
- **Region-tension dressing variants** — calmed vs. militarized signage/wreckage density (Module 1 §4) — implemented as `UsdVariantSets` on the dressing kit (author-time selection), not new geometry (§2.4 covers why this stays out of runtime USD authoring).

### 1.4 Threat Zone / Hazard Entities (Module 4 §3.2)

| Hazard | Geometry need |
|---|---|
| **Checkpoint** | Barricade + gate-arm (hinged) + guard booth |
| **Pursuit** | Pursuer vehicle(s) — **reuses the Phase 3 vehicle chassis kit** (generic pursuer skin, not a new vehicle type) |
| **Ambush Point** | Roadblock debris / cover props (built from the Prop kit, §1.5) |
| **Hot Zone** | Mostly a gameplay trigger volume (Profile-monitoring), with a light visual tell (watchtower/camera prop) — no dedicated collision geometry needed |
| **Convoy Backup escort** | Reuses the Phase 3 vehicle chassis kit (generic escort skin) — Module 3 §4 explicitly says this reuses the threat-zone pursuer AI/entity budget, so it should reuse the *asset* budget too |

### 1.5 Props (world dressing, Pillar 4 — diegetic consequences)

- Roadside wreckage variants (calmed vs. militarized).
- Signage kit (dispatch-board flavor signage, regional graffiti/propaganda).
- Small clutter kit (barrels, loose crates, debris) — reuses Cargo Container shell kit geometry where sensible (a "damaged crate" prop *is* a cargo crate mesh, just placed as static dressing).
- Checkpoint/patrol dressing (tents, barrier stacks) shared with the Hazard category's Checkpoint asset.

### 1.6 Runners / Characters (placeholder now, on-foot hooks reserved)

**Now (in scope for Phase 2, see §3):** each of the 6 roster runners gets a trivial placeholder proxy — a flat billboard card (portrait-image texture, always-faces-camera or simply front-facing) or a plain capsule mesh, whichever reads better standing in a vehicle seat or a dispatch-board scene. No skeleton, no walk cycle, no per-runner silhouette modeling. Authored under a new `Character` category (§2.1/§2.7) so the naming/hardpoint conventions it needs already exist before any real geometry does.

**Reserved, not scheduled (future):** the producer wants to keep open the possibility of a runner acting independent of their vehicle — leaving it parked to sneak into a location on foot, or commandeering a second, unattended vehicle to run interference/decoy for the one actually carrying cargo. Neither mechanic is committed content in Phases 0–5, but two cheap architectural hooks go in now specifically so this stays possible later without revisiting already-shipped assets:

- **Vehicle mount/dismount hardpoints** — every vehicle (Phase 3) gets `Hardpoints/DriverSeat` and `Hardpoints/ExitPoint` markers (§2.3), the same way cargo beds already get `TieDown_NN` markers. A placeholder character parented to `DriverSeat` today, or unparented at `ExitPoint` in a future on-foot build, needs zero vehicle-asset rework either way — the hardpoint is the contract, not the geometry behind it.
- **Vehicle-agnostic driver identity** — nothing in the Phase 3 vehicle spec assumes a specific driver (player runner vs. AI pursuer/escort skin, §1.4); the same chassis asset already serves both, which is exactly the property "commandeer any nearby vehicle" would need if it's ever built — no new vehicle variant class required for that mechanic, only new gameplay logic.

A full "Phase 6" for humanoid rigging, on-foot locomotion/stealth animation, and vehicle mount/dismount runtime logic is named at the end of §3 as a placeholder for that future work — deliberately not scoped in detail here, since Version 0 of the game design has no on-foot mission content to build it against yet.

### 1.7 Cross-category modularity summary

The same four kits recur under every category, which is the intended payoff of "modular sub-components" (CLAUDE.md constraint #2):

1. **Hardpoint/tie-down convention** — used by Cargo (pallets), Vehicles (beds, and now driver seat/exit points), and Characters (anchor point) identically.
2. **Hinge/latch convention** — used by Vehicles (doors, cargo latches) and Hazards (checkpoint gate arms) identically.
3. **Tile-snap convention** — used by Terrain exclusively, but its trigger-marker sub-pattern (§2.3) is reused by Hazards (Hot Zone, Ambush Point) for placement markers.
4. **Prop/dressing kit** — shared raw material between Terrain (biome dressing), Hazards (Ambush cover, Checkpoint tents), and Props (clutter, wreckage) — one kit, many placements.

---

## 2. Standardized USD Prim Hierarchy & Rigging Spec

### 2.1 Root structure (every asset)

```
/<Category>_<AssetName>                 Xform, default prim  e.g. /Vehicle_Mule, /Cargo_GlassCase, /Terrain_Washout
  /Geometry                             Scope — static, non-animating render meshes
  /Rig                                  Scope — animatable pivot Xforms (only on assets that need them)
  /Hardpoints                           Scope — non-rendering marker Xforms (tie-downs, mounts, triggers)
  /Collision                            Scope — simplified physics-proxy meshes
  /Materials                            Scope — UsdShade.Material library (already `usd_utils.get_material()`'s convention)
```

`<Category>` is one of `Vehicle`, `Cargo`, `Terrain`, `Hazard`, `Prop`, `Character`. This keeps every asset's default prim self-describing when flattened/inspected standalone (e.g. in `usdview` or a bug report), and gives the glTF exporter a predictable single root node per asset.

**`Character` is a reserved, minimal-content category for now** (§1.6) — a placeholder asset (`/Character_MaraItoh`, etc.) only needs `Geometry` (the capsule/billboard proxy) and `Hardpoints/Anchor` (the single point that aligns to whichever vehicle `Hardpoints/DriverSeat` it's parented to, or to world space when standing on foot in a future build). `Rig` and `Collision` stay empty/unused until real humanoid geometry replaces the placeholder — the scope skeleton exists so that swap doesn't require renaming or restructuring anything referencing the character asset.

### 2.2 Rig scope — animatable entities

CLAUDE.md requires: *steerable front wheels, rotating axles, articulated suspension, opening doors, latching cargo bay locks*. All of these are **pivot Xforms**, nested so the pivot is always the parent of the mesh it moves (a glTF node only inherits its own transform channel correctly if authored this way — animating a mesh prim directly, instead of a parent Xform, is the classic mistake that produces meshes that don't rotate about the right point after export):

```
/Vehicle_Mule/Rig/Wheel_FL_Steer            Xform (rotateY — steering)
  /Wheel_FL_Spin                            Xform (rotateX — wheel spin)
    /Wheel_FL_Mesh                          Mesh (child of the pivot it needs to spin around)
/Vehicle_Mule/Rig/Wheel_RL_Spin             Xform (rotateX only — rear axle, no steer pivot)
  /Wheel_RL_Mesh
/Vehicle_Mule/Rig/Door_Rear_Hinge           Xform (rotateY — door swing)
  /Door_Rear_Mesh
/Vehicle_Mule/Rig/CargoLatch_Hinge          Xform (rotateX — latch flip)
  /CargoLatch_Mesh
```

**Naming convention — pivot suffixes are load-bearing, not cosmetic.** Every pivot Xform ends in one of a small fixed set of suffixes: `_Steer`, `_Spin`, `_Hinge`, `_Latch`. The Babylon runtime looks these up by **suffix pattern**, not a hardcoded per-vehicle node list (e.g. "find every `TransformNode` whose name ends in `_Spin` and drive it from wheel angular velocity") — this is what lets one piece of runtime animation-driving code work across all 5 vehicles (and future roster additions) without per-asset runtime code. Laterality uses `_FL/_FR/_RL/_RR` (front-left, front-right, rear-left, rear-right), matching common vehicle-rig convention.

### 2.3 Hardpoints scope — non-rendering markers

Zero-geometry Xforms (translate-only, no mesh child) whose **world position is the payload**, not their appearance:

```
/Vehicle_Mule/Hardpoints/TieDown_01 .. _04      # bed tie-down points
/Cargo_GlassCase/Hardpoints/TieDown_01 .. _04   # matching convention on the cargo side
/Vehicle_Mule/Hardpoints/DriverSeat             # runner mount point (§1.6) — every vehicle gets one
/Vehicle_Mule/Hardpoints/ExitPoint              # where a dismounted runner appears alongside the vehicle
/Character_MaraItoh/Hardpoints/Anchor           # the character-side point that aligns to DriverSeat/ExitPoint
/Terrain_Washout/Hardpoints/ConnectIn           # tile-snap edge marker
/Terrain_Washout/Hardpoints/ConnectOut
/Hazard_HotZone/Hardpoints/TriggerCenter        # placement marker for the gameplay-side trigger volume
```

Tie-down points are named identically (`TieDown_01`..`TieDown_04`) on both the vehicle-bed side and the cargo side specifically so a future loadout-assembly script can align a cargo prim into a vehicle-bed prim by matching hardpoint names/counts, rather than hand-placed per pairing. `DriverSeat`/`ExitPoint`/`Anchor` follow the same logic one level up: a runner (placeholder or, later, a real rigged character) is positioned by matching its `Anchor` to a vehicle's `DriverSeat`, not by any vehicle- or character-specific placement code — the same reason this pays off for cargo pays off here for the future on-foot mechanic (§1.6), at effectively zero cost today since it's one more marker Xform per vehicle.

### 2.4 Metadata strategy — the one open risk this roadmap flags explicitly

CLAUDE.md asks for "custom metadata attributes for physics/gameplay" on the standardized prim tree. USD supports this natively via `customData` (e.g. `prim.SetCustomDataByKey("harshDeliveries:tieDownCapacityKg", 250)`), authored under a `harshDeliveries:` namespace for documentation/authoring-time clarity.

**The risk:** this pipeline's web-facing artifact is not the `.usdz` — it's a `.glb` produced by round-tripping through headless Blender (`export_utils.export_gltf()`). Whether Blender's glTF *exporter* (as opposed to its USD *importer*, which is what's been stress-tested so far per the `usd-dcc-export` skill) preserves arbitrary USD `customData` as glTF node `extras` has **not been verified in this codebase yet**. glTF node *names* are known to survive (Blender preserves object names into glTF node names, modulo its own sanitization of invalid characters), but `extras` survival is a second, separate, unverified claim.

**Resolution (validate, don't assume):** Phase 1 includes an explicit test of this exact question. Depending on the result:
- **If `customData` survives as glTF `extras`** readable from Babylon's loaded node data — great, author metadata directly on the USD prims per the `harshDeliveries:` namespace above, and skip the fallback below.
- **If it doesn't** (the more likely outcome, since Blender's glTF exporter's "Custom Properties" export option is a Blender-property concept, not a direct USD-customData passthrough) — fall back to a **generated sidecar manifest**: the same Python asset script that authors the USD also writes `<name>.manifest.json` next to `<name>.glb`, keyed by the same prim/node names (`TieDown_01`, `Wheel_FL_Steer`, etc.), carrying whatever gameplay/physics values would otherwise have lived in `customData`. This keeps the source of truth in one authored Python script (no hand-maintained duplicate data file), and the Babylon runtime reads the manifest alongside the glb rather than trying to mine glTF extras.

Either way, **node names are the stable cross-format contract** — that's why §2.2/§2.3's naming conventions are specified as strictly as they are; they're the join key regardless of which metadata path wins.

### 2.5 Collision scope

Simplified proxy meshes (boxes/cylinders via `usd_utils.make_box_mesh`/`make_cylinder_mesh`, not the render mesh itself), named `Collision/Hull_*`, kept in their own scope so the Babylon runtime can load them, use them to build Havok physics impostors, and hide them from the render pass — as opposed to running physics against full render-detail geometry. Cargo Integrity (Module 1 §6.1) is explicitly meant to be read off the vehicle's existing physics signals (impulse magnitude, suspension compression), so vehicle collision hulls are the load-bearing physics geometry in this pipeline, not a nice-to-have — Phase 3 should treat them as a required deliverable per vehicle, not deferred polish.

### 2.6 Terrain tile snap convention

Every terrain tile is authored so its default-prim origin sits at the tile's "entry" edge, with a fixed tile unit length (a single constant, defined once in `usd_utils.py` or a new `terrain_utils.py`, e.g. `TILE_LENGTH = 20.0` meters), and a matching `ConnectOut` hardpoint marker at the far edge at exactly `(0, 0, TILE_LENGTH)` in local space. Chaining tiles at level-assembly time is then pure translation along the previous tile's `ConnectOut` position — no per-tile custom alignment math, and no risk of authored gaps/overlaps silently drifting as more tile types are added in Phase 4/5.

---

## 3. Phased Implementation Roadmap

Each phase is scoped to fit one focused development session and produces a concrete, independently-testable artifact — per Module 4's Version 0 close-out recommendation to validate the pipeline cheaply (vertical slice) before committing to full six-runner/five-vehicle/five-tier scope.

### Phase 0 — Core OpenUSD Utility Library
**Builds on:** existing `pipeline/usd_utils.py` + `pipeline/export_utils.py` (already implement stage setup, box/cylinder mesh authoring, material caching, PointInstancer baking, usdz/glb export).

**New work:**
- **Rig helpers** (`pipeline/rig_utils.py`): `add_pivot_xform(parent, name, suffix)` enforcing the `_Steer/_Spin/_Hinge/_Latch` suffix convention from §2.2; rotate-op helpers for steering/spin/hinge axes.
- **Hardpoint helpers**: `add_hardpoint(parent, name, translate)` for zero-geometry marker Xforms (§2.3).
- **UV mapping helpers**: `make_box_mesh`/`make_cylinder_mesh` currently author geometry + normals but **no `primvars:st`** — needed for any textured material beyond flat color (livery decals, region-dressing signage). Add UV authoring to both, plus a `make_mesh` variant that accepts explicit UVs for hand-authored parts.
- **Material palette extension**: `get_material`/`set_color` currently key purely on flat RGB. Extend with roughness/metallic presets (paint, rubber, glass-preview, unmarked-matte, steel) so cargo/vehicle materials read as differentiated in Blender/Babylon preview without needing texture painting yet.
- **Manifest helper** (`pipeline/manifest_utils.py`): `write_manifest(path, data)` — the generated sidecar JSON described in §2.4, ready regardless of which way Phase 1's customData-survival test resolves.
- **Standard root/scope builder**: `create_asset_stage(category, name)` wrapping `usd_utils.create_stage()` to produce the §2.1 scope skeleton (`Geometry`/`Rig`/`Hardpoints`/`Collision`/`Materials`) consistently, the way `create_stage()` already standardizes up-axis/meters-per-unit/default-prim.

**Acceptance criteria:**
- A trivial hand-written test asset (one box "chassis," one box "wheel" on a `_Spin` pivot, one `TieDown_01` hardpoint) builds via the new helpers only.
- `usdchecker` clean on the flattened output.
- `usdtree` shows the exact §2.1/§2.2/§2.3 scope structure.
- UV primvars present and valid (`usdchecker`'s primvar checks pass) on a textured test box.

### Phase 1 — Basic Test Prims & Build Pipeline Validation
**Purpose:** prove the *entire* pipeline round-trip end-to-end on trivial geometry before any real asset production, and **resolve the §2.4 metadata-survival question** — this phase is explicitly a spike, not production content.

**Work:**
- Build one minimal articulated test asset using Phase 0 helpers: a box chassis, one `_Steer`→`_Spin` wheel pivot chain, one `_Hinge` door, one `Hardpoints/TieDown_01`, one `customData` gameplay attribute (e.g. `harshDeliveries:testValue`).
- Run the full export chain: `usdchecker` → `export_usdz()` → `export_gltf()` (headless Blender) → inspect the resulting `.glb` directly (a short script using Blender or a glTF-JSON inspection, per the `usd-dcc-export` skill's §5 "headless Blender as a diagnostic tool" pattern) for: node names (do `_Spin`/`_Hinge`/`TieDown_01` survive, sanitized or not?), transform hierarchy (is the pivot still the parent?), and whether `extras` carries the customData.
- Load the resulting `.glb` in the actual Babylon runtime (`src/main.ts`'s existing `AppendSceneAsync` path) and confirm: the scene renders, and a small ad hoc test script can find the `_Spin` node by name and rotate it at runtime (proves the naming-convention-based lookup strategy from §2.2 actually works end-to-end, not just in theory).
- Based on the customData/extras result, **lock in** the Phase 0 manifest helper as required-path or optional/unused, and note the decision in this document's changelog (§4 close-out convention, mirroring how the game-design docs handle their own decisions log).

**Acceptance criteria:**
- `.glb` loads and renders in the Babylon dev server (`npm run dev`) with zero console errors.
- The `_Spin` pivot rotates correctly about its intended axis when driven from a throwaway runtime test script (delete after confirming — this phase validates the pipeline, it doesn't ship the test asset).
- Written finding (a short note, this doc or a follow-up) on customData/extras survival, since Phase 2+ metadata authoring depends on knowing which path to use.
- `npm run check` still passes (no TypeScript/build regressions from the throwaway test script, which should not be committed as-is).

### Phase 2 — Modular Cargo & Prop Engine
**Builds on:** Phase 0 helpers, Phase 1's confirmed hardpoint/manifest strategy.

**Work:**
- Cargo container kit (§1.2): crate, drum, glass case, sealed container, machine-parts crate — all sharing the pallet-base + `TieDown_01..04` hardpoint convention.
- Prop kit (§1.5): signage, wreckage (two dressing states per §1.3's variant note), barricade/checkpoint booth static geometry (rigging deferred to Phase 5 alongside the gate-arm hinge, since Checkpoint's *hinge* needs the Phase 0 rig helpers exercised on a non-vehicle asset first — worth doing once here rather than assuming vehicle-only).
- Multi-unit stacking test: one pallet stacked 3–4 high via `PointInstancer`, then baked per `export_utils.bake_all_point_instancers()` before export.
- **Placeholder Character kit (§1.6):** one capsule-or-billboard proxy per roster runner (6 total, Module 2 §2), authored under the `Character` category (§2.1) with a single `Hardpoints/Anchor` marker — no rig, no per-runner sculpted likeness. Portrait-image texture (if using the billboard-card variant) can be a flat placeholder color/initial per runner at this stage; swapping in real portrait art later is a texture change, not a re-author.

**Acceptance criteria:**
- Every cargo container type exports a clean `.usdz` + `.glb` pair; `TieDown_01..04` hardpoints present and positioned consistently across all container variants (so a later loadout-assembly script can treat them interchangeably).
- Stacked-pallet test asset's baked instances are visually correct in Blender (no leftover/duplicate/mispositioned geometry — the exact failure mode `usd-dcc-export` §3 warns about) and in the Babylon-loaded `.glb`.
- Visual differentiation check in a read-only viewport (`usdview` or Blender): glass reads as distinct from steel drum reads as distinct from wood crate, using only the Phase 0 material-preset extension (no texture painting required yet).
- All 6 placeholder character proxies export clean `.usdz`/`.glb` pairs with an `Anchor` hardpoint present; one proxy manually aligned to a stand-in `DriverSeat` position confirms the anchor-matching approach (§2.3) before Phase 3 commits to authoring it on every vehicle.

### Phase 3 — Vehicle Chassis & Suspension Rigging Engine
**Builds on:** Phases 0–2 (cargo beds need the same hardpoint convention cargo containers already have).

**Work:**
- Shared kit build-out per §1.1: chassis frame builder (parametric, scalable per vehicle class), wheel assembly (steerable-front / fixed-rear per §2.2), suspension mount points, cargo bed/box variants (open/enclosed/armored/trunk/sidecar), door/hatch hinge kit, cargo latch kit, lighting/livery prop kit.
- Assemble the 5 roster vehicles (Mule, Goat, Needle, Bastion, Wasp) from the shared kit, parameterized per Module 2 §3/§4's stated axes (Capacity → bed footprint, Durability → frame/plating thickness, Profile → size/color/conspicuousness, Terrain Traction → tire width/tread style).
- Author `Collision/Hull_*` proxies per vehicle (§2.5) — required this phase, since Cargo Integrity's physics-signal approach (Module 1 §6.1) depends on it existing, not on render-mesh collision.
- Author `Hardpoints/DriverSeat` and `Hardpoints/ExitPoint` on every vehicle (§1.6, §2.3) — cheap, mechanically inert today, and the specific hook that keeps the future on-foot/commandeer-a-second-vehicle direction from requiring a revisit of already-shipped vehicle assets.

**Acceptance criteria:**
- All 5 vehicles export clean `.usdz`/`.glb` pairs with `_Steer`/`_Spin`/`_Hinge`/`_Latch` pivots present and correctly parented (mesh is always a child of its pivot, per §2.2).
- Babylon-side test: for at least one vehicle, drive `_Steer` and `_Spin` nodes from a throwaway script and confirm visually correct steering + rolling behavior (front wheels turn about a vertical axis at the wheel's own position, not the vehicle's center).
- Each vehicle's silhouette read-check in a viewport confirms it's visually distinguishable from the others at a glance (a Bastion should not be mistakable for a Mule) — a soft but real check, since Module 2's design explicitly relies on players recognizing vehicle identity, not just stats.
- `usdchecker` clean on every vehicle; `Collision/Hull_*` present on every vehicle.
- `DriverSeat`/`ExitPoint` present on every vehicle at a sensible in-cab/beside-the-vehicle position; one Phase 2 placeholder character's `Anchor` aligns onto each vehicle's `DriverSeat` without per-vehicle special-casing, confirming the hardpoint-matching contract from §2.3 holds across the whole vehicle roster, not just the one vehicle it was designed against.

### Phase 4 — Environmental & Terrain Block Generator
**Builds on:** Phase 0 (tile-snap constant, §2.6), Phase 2's prop-kit patterns (biome dressing reuses the same authoring approach).

**Work:**
- Road tile kit: straight, curve, junction, plus the four named terrain hazards (Washout, Ridge Line, Bog Crossing, Blind Switchback) as tile variants/specializations, each carrying `ConnectIn`/`ConnectOut` hardpoints per §2.6.
- Regional biome dressing kits (neutral, Highland/mountain, swamp, dockside) layered onto the generic tile kit.
- Region-tension dressing variants via `UsdVariantSets` (calmed vs. militarized) — author-time selectable, not runtime-dynamic (see §2.4's rationale: this is static per-build-of-the-scene, unlike cargo integrity which is genuinely runtime state).
- Route-width/traction gameplay tags per tile, via whichever of customData/manifest Phase 1 confirmed.

**Acceptance criteria:**
- A short test route (5–6 chained tiles including one of each hazard type) assembles via translation-only tile chaining with zero authored gaps or overlaps at each `ConnectOut`→`ConnectIn` join.
- The Ridge Line tile's authored width is narrow enough to visibly gate out non-Wasp vehicle profiles when both are viewed side-by-side in a viewport (a concrete check against Module 2 §5's "Iveta + Wasp unlocks a route other loadouts can't attempt" design intent) — this is a geometry-width sanity check at asset-authoring time, not a runtime collision test.
- Both `UsdVariantSets` states (calmed/militarized) selectable and visually distinct on the same dressing kit instance.

### Phase 5 — Advanced Level-Specific Assets & Complex Hazards
**Builds on:** Phases 2–4 almost entirely by reuse — this phase should add the *least* new geometry of any phase, per Module 4 §6's explicit design note ("reuse catalog entries rather than inventing new named hazards per mission").

**Work:**
- Checkpoint asset: barricade + hinged gate-arm (first non-vehicle use of the `_Hinge` rig convention) + guard booth, using Phase 2's prop-kit geometry patterns.
- Pursuit/Convoy-Backup vehicle skins: generic pursuer and generic escort, built as **material/livery variants of the Phase 3 chassis kit**, not new chassis — directly exercising Module 3 §4's note that Convoy Backup "reuses the same pursuer/escort AI budget" (this roadmap extends that to the asset budget).
- Ambush Point cover props and Hot Zone watchtower/marker prop, from the Phase 2 prop kit.
- Assemble the concrete Module 4 §5.5 tier-5 composite test case (Ridge Line + Pursuit at the same location) purely from Phase 3/4/5 pieces, as the roadmap's own integration test.

**Acceptance criteria:**
- Checkpoint gate-arm hinge behaves identically (by convention, not by copy-pasted code) to the vehicle door-hinge rig from Phase 3 — same suffix, same pivot-parents-mesh structure, confirmed by the same Babylon lookup-by-suffix code path with zero asset-specific runtime branches.
- Pursuit/escort vehicles reuse a Phase 3 chassis file (referenced + re-materialed), not a duplicated/forked one — a structural check (grep the authoring script for a reference to the existing vehicle asset, not a fresh `make_box_mesh` chassis built from scratch).
- The tier-5 composite test scene (Ridge Line + Pursuit) assembles with zero new asset types beyond this phase's own additions — a direct verification of Module 4 §6's reuse principle, and the clearest sign the modularity investment in Phases 0–4 paid off.

### Phase 6 (Deferred, not scheduled) — Character Rigging & On-Foot Mechanics

**Not part of this roadmap's committed scope.** Named here only so the reserved `Character` category (§1.6, §2.1) and the `DriverSeat`/`ExitPoint`/`Anchor` hardpoints (§2.3) authored starting in Phases 2–3 have a stated destination, rather than looking like unexplained scope creep in those earlier phases. Would cover, whenever it's actually greenlit:

- Full rigged humanoid geometry (skeleton + skinning) per runner, replacing the Phase 2 placeholder proxies — a materially different pipeline problem than this roadmap's hard-surface modular kits, since it exercises skinning/animation through the Blender glTF conversion path in a way nothing in Phases 0–5 does.
- Walk/idle/sneak locomotion and vehicle mount/dismount animation, keyed off the same `DriverSeat`/`ExitPoint`/`Anchor` hardpoint contract already in place.
- Runtime logic (not an asset concern) for leaving a vehicle parked and unattended, on-foot stealth detection (likely reusing the Hot Zone/Profile-monitoring concept from Module 4 §3.2, extended to a walking character), and commandeering a second, unattended vehicle.
- A design pass in `docs/game-design/` justifying and specifying this as actual mission content — Version 0 (Modules 1–4) has no on-foot objective variant today, so this phase also has no mission spec to build against yet. That design work should happen before Phase 6 is scheduled, not during it.

---

## 4. Phase Verification & Quality Criteria

Common gates every phase must clear, in addition to each phase's specific acceptance criteria above:

| Gate | How it's checked |
|---|---|
| **Spec validity** | `usdchecker` clean on the flattened layer or final `.usdz` (per CLAUDE.md's Asset Pipeline validation rule) — necessary but not sufficient. |
| **Hierarchy correctness** | `usdtree` output matches the §2.1 scope skeleton exactly (`Geometry`/`Rig`/`Hardpoints`/`Collision`/`Materials`), and every `Rig` pivot is confirmed to be the *parent*, not a sibling, of the mesh it moves. |
| **Downstream render correctness** | Visual check in a read-only viewport (`usdview` and/or headless-Blender screenshot per `usd-dcc-export` §5) — passing `usdchecker` alone does not prove this (see that skill's opening line: "a spec-valid, usdchecker-clean USD file can still render incorrectly in downstream consumers"). |
| **glTF export integrity** | `export_gltf()` completes without error; resulting `.glb` loads in the actual Babylon dev harness (`npm run dev`) with zero console errors — not just "Blender didn't crash." |
| **Naming-convention compliance** | Every animatable pivot ends in `_Steer/_Spin/_Hinge/_Latch`; every hardpoint follows the `TieDown_NN`/`ConnectIn`/`ConnectOut`/`TriggerCenter` conventions from §2.2/§2.3/§2.6 — this is what keeps Babylon's lookup code asset-agnostic, so drift here silently breaks the "no per-asset runtime code" payoff. |
| **No stray/leftover geometry** | Any baked `PointInstancer` or deactivated prim checked per `usd-dcc-export` §3's active-vs-visible distinction — `SetActive(False)`, never a bare invisible hint, on anything meant to be fully gone. |
| **Build verification** | `npm run check` passes after any runtime-side test code from a given phase (throwaway test scripts should be removed, not committed, once their validation purpose is served). |

**Cross-phase regression note:** because Phases 2–5 all consume Phase 0's shared helpers, a helper change made *during* a later phase (e.g. discovering Phase 0's UV-mapping helper needs a fix while building Phase 3's vehicles) should be re-validated against Phase 1's and Phase 2's existing assets before moving on — the modularity this roadmap is built around is exactly what makes a Phase 0 regression silently propagate everywhere at once if it isn't re-checked.

---

## Decisions Log
- **Runner/character 3D models: placeholder now, architecture reserved for on-foot gameplay later (confirmed by producer).** Not full-detail production content in Phases 0–5 — a capsule/billboard proxy per runner is enough for now — but the producer explicitly wants the option open to have a runner act independent of their vehicle (sneak on foot, commandeer a second vehicle as a decoy/escort for the cargo vehicle), so the `Character` category, its `Anchor` hardpoint, and every vehicle's new `DriverSeat`/`ExitPoint` hardpoints are authored starting now (Phases 2–3) specifically so that later work is a content addition, not an architecture change. Full humanoid rigging itself stays deferred (see "Phase 6 (Deferred)" at the end of §3) pending an actual on-foot mission design pass, which doesn't exist yet in Version 0.
- **Metadata channel (customData vs. sidecar JSON manifest) left as a Phase-1-validated decision, not asserted here** — the existing pipeline has only stress-tested Blender's USD *import* path (per `usd-dcc-export`), not its glTF *export* path's `extras` fidelity; Phase 1 is scoped specifically to resolve this before Phase 2+ commit to authoring gameplay metadata one way or the other.
  - **Addendum (Phase 1, validated):** `customData` does **not** survive — confirmed with a headless-Blender diagnostic that the break is at *import*, not export: right after `bpy.ops.wm.usd_import()`, the Blender object for a prim carrying `harshDeliveries:testValue` in USD has an empty custom-property set (`obj.keys() == []`). Blender's USD importer has no concept mapping USD `customData` to Blender custom properties, so no glTF exporter setting (`export_extras` included) can surface it — the exported `.glb`'s JSON chunk has zero `extras` keys anywhere. glTF node *names* do survive verbatim (confirmed unsanitized for this test asset's names). **Resolution: the sidecar manifest (`pipeline/manifest_utils.write_manifest`) is the required path for Phase 2+ gameplay metadata authoring** — every future asset script should call it alongside its `.glb`/`.usdz` export, keyed by the same prim/node names per §2.4's own convention.
  - **Second Phase 1 finding, same investigation (deviation from the written prompt, flagged for review):** the roadmap's own §2.2 worked example — a `_Spin` pivot nested directly under a `_Steer` pivot at the same local point (zero relative translate) — does not round-trip through this pipeline's Blender-based glTF export by default. `rig_utils.add_pivot_xform()` only authors a translate op when the translate argument is non-zero, so a zero-offset `_Spin` pivot is a USD `Xform` with no authored xformOps at all. Blender's `wm.usd_import` operator defaults `merge_parent_xform=True` ("Allow USD primitives to merge with their Xform parent if they are the only child in the hierarchy"), which elides exactly this shape — an identity-transform Xform with a single child — reparenting the child mesh up a level and silently dropping the pivot node before glTF export ever runs. `usdchecker`/`usdtree` on the USD side show nothing wrong, since the USD file itself is correct; the loss is downstream-consumer-specific, the same category of gap the `usd-dcc-export` skill already documents for `PointInstancer` and implicit-Gprim bindings. **Fix applied and verified:** `pipeline/blender_usd_to_gltf.py` now passes `merge_parent_xform=False` to `bpy.ops.wm.usd_import(...)`; re-running the Phase 1 test asset confirms `Wheel_FL_Spin` survives as its own glTF node, correctly parented between `Wheel_FL_Steer` and `Wheel_FL_Mesh`. This is a shared-pipeline-code change beyond this prompt's literal "write a throwaway script" scope, made because the naming-lookup-by-suffix strategy this whole roadmap depends on (§2.2) does not work at all without it for the common zero-offset-pivot case — flagging for the next review rather than silently absorbing it as an unstated Phase 0 fix.
- **Vehicle collision hulls treated as required Phase 3 deliverables, not deferred polish** — Cargo Integrity (Module 1 §6.1) is explicitly designed to read off vehicle physics signals the engine already tracks, which makes collision geometry load-bearing for a core mechanic, not an optimization.

---

*This document is the architecture/roadmap deliverable requested against `docs/game-design/` Modules 1–4 (Version 0). Per that design set's own close-out note, treat this as a baseline to diff against as implementation proceeds, not to silently rewrite — if a phase's plan changes materially once building starts, prefer a short addendum noting what changed and why over editing this file's history in place.*
