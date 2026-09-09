---
name: usd-vehicle-assembly
description: Use when authoring OpenUSD Python scripts for vehicles, machinery, or any asset with moving parts (wheels, arms, turrets, hatches, suspension) or swappable configurations (wheel types, attachments, covers). Complements usd-build and usd-dcc-export.
allowed-tools: Bash, Read, Edit, Write, Grep, Glob
---

# Vehicle/Machinery Asset Authoring (this repo's pipeline)

This repo's asset pipeline is **bake-and-play**, not live-physics: `pipeline/export_utils.py`
flattens the authored stage, converts it via headless Blender
(`bpy.ops.export_scene.gltf(export_animations=True, ...)`, see `blender_usd_to_gltf.py`), and
the web runtime (Babylon.js + Havok, or three.js) loads the resulting `.glb` — it never loads
USD/usdz directly (see `usd-dcc-export`). Nothing downstream evaluates USD schemas at runtime.

A generically-reasonable USD authoring proposal for vehicles/machinery (e.g. one written for an
Omniverse/PhysX-style live-USD-physics pipeline) will contain rules that silently do nothing in
*this* pipeline. The rules below are reframed for what actually survives flatten → Blender →
glTF → Babylon/three.js.

## 1. Assembly hierarchy: Root Xform -> Chassis -> Kinematic sub-assembly -> Leaf geometry

Keep this discipline — it's orthogonal to physics and pays off on the web-runtime side:

```
/Vehicle (Xform, default prim)
  /Chassis (Xform)
    /Body (Mesh)
    /Collision (Scope)          -- see section 2
  /FrontLeftWheel (Xform)       -- own Xform prim, not baked into Body's mesh points
    /Wheel_Visual (Mesh)
    /Wheel_Collision (Mesh)
  /Turret (Xform)
    /Turret_Visual (Mesh)
```

Every part that needs to move at runtime (in Babylon/three.js code, or via baked animation) must
be its **own `UsdGeom.Xform` prim**, not geometry baked into a parent mesh's points. Blender's USD
importer creates one object per prim, and each object becomes its own glTF node — a node is the
smallest thing you can target by name, animate, or attach a runtime constraint to. Baking a wheel's
geometry into the chassis mesh makes it physically unable to move independently downstream, no
matter what you do in USD.

**Naming: keep every prim name that must survive as a matchable node globally unique across the
whole stage, not just unique within its parent.** USD namespaces are hierarchical (two prims can
both be named `Wheel` if they have different parents), but Blender's object namespace is flat —
importing two identically-named leaf prims from different branches produces auto-suffixed
duplicates (`Wheel`, `Wheel.001`), which then propagate as differently-named glTF nodes. Any
runtime code that looks up a node by exact name (`scene.getMeshByName('Wheel_Collision')`) breaks
silently for the second instance. This has not been empirically re-verified in this repo the way
the `usd-dcc-export` findings were — confirm actual exported node names (e.g. inspect the loaded
Babylon/three.js scene's mesh names, or `usdtree`/`gltf-transform inspect` on the flattened output)
before depending on an exact-name lookup in runtime code. Prefer names like `FrontLeftWheel_Visual`
over nested-but-locally-named `Wheel/Visual` for anything you intend to find by name later.

## 2. Collision geometry: a real low-poly Mesh, not `UsdPhysics.CollisionAPI`

The instinct to keep a separate, simplified collision shape from the high-poly visual mesh is
correct. Applying `UsdPhysics.CollisionAPI` (`convexHull`/`orientedBox`) to express it is not —
nothing in this pipeline reads UsdPhysics schemas. Blender's glTF exporter doesn't translate them,
and Babylon's Havok integration builds physics shapes in TypeScript from mesh data
(`PhysicsShapeConvexHull`, `PhysicsShapeMesh`, ...), not from USD schema.

Instead:

- Author the collision shape as a plain low-poly `UsdGeom.Mesh` (use `usd_utils.make_box_mesh` /
  `make_cylinder_mesh`, or a hand-authored low-poly hull) as a **sibling** of the visual mesh, under
  a `Collision` `UsdGeom.Scope` per part, e.g. `/Vehicle/Chassis/Collision/Chassis_Collision`.
- Give it a name ending in a stable suffix (e.g. `_Collision`) so runtime code can find it by
  substring/suffix match after load, rather than relying on an exact hand-maintained list.
- **Do not rely on `visibility=invisible` to hide it in the exported `.glb`.** The `usd-dcc-export`
  skill already documents that USD visibility is only a hint some consumers (three.js-based tools)
  ignore outright; there's no confirmed guarantee here that Blender's glTF exporter preserves an
  imported hidden/invisible state the way you'd want either. Instead, author it as an ordinary
  visible mesh in USD, and have Babylon/three.js runtime code hide it after load (Babylon:
  `mesh.isVisible = false` on every node matching the collision-name convention) while using its
  vertex data to build the physics shape. This makes hiding-for-render an explicit runtime decision
  instead of a hope that an authoring-time hint survived two format conversions.
- Don't add `UsdPhysics.CollisionAPI`/`RigidBodyAPI`/etc. to these prims — they cost authoring time
  for zero runtime effect in this pipeline. If a future consumer *does* read USD physics directly
  (e.g. an Omniverse review pipeline), add them then, additively, without changing this convention.

## 3. Moving parts: baked transform animation, not `UsdPhysics` joints

**Do not model wheels/arms/turrets/hatches as `UsdPhysics.PhysicsJoint` (revolute/prismatic/etc.)
with the expectation that motion survives to the web runtime.** glTF's core spec has no
joint/physics-constraint representation, `bpy.ops.export_scene.gltf` in `blender_usd_to_gltf.py`
exports no physics extension, and Babylon's glTF loader doesn't read one either. A joint-only
vehicle (no baked keyframes) will export with all parts frozen in their bind pose — the motion is
simply lost, with no error at any stage of the pipeline.

What actually survives, because `export_gltf()` is called with `export_animations=True`: time-sampled
`UsdGeom.Xformable` transform ops (rotate/translate authored per-frame with `Usd.TimeCode`). Author
looping or scripted motion (a spinning wheel, an idle turret sweep, a hatch opening) this way, on
each part's own Xform prim from section 1. This is what Blender's USD importer bakes into an
Action/F-curve and what its glTF exporter turns into a glTF animation channel Babylon/three.js can
play back.

**`UsdPhysics.DriveAPI` (motorized joints) has the same problem, one level worse** — it expresses a
*runtime-computed* target (a motor responding to live input), which baked keyframes can't represent
at all regardless of the joint issue above. If the vehicle needs true runtime-driven articulation
(player steering input driving wheel rotation, throttle-driven spin, procedural suspension response),
that has to be built as Havok constraints/motors in Babylon TypeScript code directly (see the
`babylon-engine` skill for Havok setup), using the pivot points and node hierarchy authored in USD
section 1 as the geometric reference — not by attempting to carry `UsdPhysics` joints/drives through
this pipeline; there is no translation step for them today.

## 4. Variant sets for swappable configurations: keep, resolve before export

`Usd.VariantSets` (wheel types, arm attachments, engine covers, ...) fit this pipeline cleanly,
because variant selection is an **authoring-time** operation here, not a runtime one — the build
script selects a variant, then flattens and exports. Each desired configuration becomes its own
`.glb` (e.g. `vehicle_offroad_wheels.glb`, `vehicle_street_wheels.glb`), not a single `.glb` the web
runtime switches at runtime:

```python
variant_set = vehicle_prim.GetVariantSets().GetVariantSet("WheelType")
for wheel_type in ("OffRoad", "Street"):
    variant_set.SetVariantSelection(wheel_type)
    with variant_set.GetVariantEditContext():
        # author or reference the wheel-type-specific geometry here
        ...
    export_gltf(stage, MODELS_DIR / f"vehicle_{wheel_type.lower()}.glb")
```

If the game needs to swap configurations at runtime (not just ship different prebuilt vehicles),
that means loading a different `.glb`/asset container per configuration in Babylon/three.js code —
still driven by which variant was selected at build time, not by any live USD variant switch.
