---
name: usd-dcc-export
description: Use when exporting/flattening an OpenUSD (pxr) scene for import into DCC tools or viewers (Blender, glTF/usd2gltf, usdz-viewer.net, three.js/Babylon.js-based web loaders) and geometry is missing, animation is missing, stray leftover geometry appears, or colors/materials don't show. Complements usd-build.
allowed-tools: Bash, PowerShell, Read, Edit, Write, Grep, Glob
---

# OpenUSD -> DCC Tool Export & Troubleshooting

Lessons from a real debugging session (modular-tank-learning-project, 2026-09-05):
a spec-valid, `usdchecker`-clean USD file can still render incorrectly (or not at all)
in downstream consumers. `usdchecker` validates the USD *spec*, not renderer support.

This repo's `pipeline/export_utils.py` already implements the PointInstancer-baking
and flatten-then-package patterns described below (`bake_all_point_instancers()`,
`export_usdz()`), plus USD→glTF conversion via headless Blender
(`export_gltf()`, used because neither Babylon.js nor three.js reliably loads
USD/usdz at runtime — see section 2) — reuse these rather than re-deriving them
from scratch.

## 1. Flattening a composed stage into one self-contained file

Two equivalent ways to collapse references/variants/payloads into a single portable layer:

- CLI: `usdcat --flatten <root>.usda -o out.usdc`
- Python:
  ```python
  stage = Usd.Stage.Open(path)
  flat_layer = stage.Flatten()
  flat_layer.Export("out.usdc")
  ```

Always re-run `usdchecker` on the flattened output. Passing `usdchecker` only proves
the file is spec-valid -- it says nothing about whether Blender, three.js, or any other
consumer will actually render every prim in it (see PointInstancer section below).

Note: `Usd.Stage.CreateNew()` cannot write directly to a `.usdz` path -- USD's usdz
file format plugin is read-only ("creating package usdz layer is not allowed through
this API"). To produce a `.usdz`, flatten to a normal layer first, then package that
with `UsdUtils.CreateNewUsdzPackage(flat_layer_path, usdz_path)` -- this is what
`export_utils.export_usdz()` does.

## 2. PointInstancer is a portability landmine

Confirmed broken or inconsistent across multiple real consumers in this session:

- **Blender's native USD importer** (5.2): converts `PointInstancer` to a `PointCloud`
  object + a "Instance on Points" geometry-nodes setup. If the prototype prim is a plain
  referenced prim (no `instanceable` flag), Blender's "Collection Info" node ends up
  wired to no collection at all -- the instancer imports as an empty PointCloud and
  nothing renders. Fix: mark the prototype `instanceable = true`
  (`proto_prim.SetInstanceable(True)` in Python) so Blender's importer builds a real
  instance Collection for it.
- **usd2gltf** (pip package, v0.3.5): crashes outright on *any* `PointInstancer` prim in
  the stage, even one that is inactive/invisible -- see bug below.
- **usdz-viewer.net / three.js-based viewers**: skip `PointInstancer` prims entirely;
  instanced geometry simply never appears.
- No guarantee either web engine's own USD/usdz loader (three.js or Babylon.js) supports
  `PointInstancer` either -- treat it as unsupported for the exported `.usdz` unless you
  have verified otherwise, and bake instancers out before packaging (see `usd-build`'s
  export step and `pipeline/export_utils.py`).

### The `instanceable` flag has a sharp edge

Marking a prototype `instanceable = true` fixes Blender's PointInstancer import, but it
also makes USD hide that prim's real children behind an opaque, internal, unreferenceable
"master" prim (e.g. `/__Prototype_1`):

- `proto_prim.GetChildren()` returns `[]` even though the prim visibly has children in
  `usdtree`.
- `proto_prim.IsInstance()` is `True`; `proto_prim.GetPrototype()` gives you the master,
  but you **cannot** author a new reference arc targeting that master path -- USD raises
  `Unresolved reference prim path ... </__Prototype_N>`.
- So: never try to reference (or internal-reference) an instanceable prototype prim, or
  its master, from other code you're generating. Neither composes children.

### The portable fix: bake instances into explicit prims

When you can't trust every downstream consumer to support `PointInstancer` (the normal
case for interchange with Blender/glTF/web viewers), stop relying on instancing for the
*export* artifact and expand it into plain geometry instead. This is a lossless,
maximally-compatible transform since USD gives you everything needed to reconstruct it
exactly. `pipeline/export_utils.py`'s `bake_point_instancer()` / `bake_all_point_instancers()`
already implement this; the shape of it:

```python
from pxr import Sdf, Usd, UsdGeom

def bake_point_instancer(stage, instancer_prim):
    instancer = UsdGeom.PointInstancer(instancer_prim)

    # Don't reference the prototype prim itself if it's instanceable (see above).
    # Read its ORIGINAL plain asset reference instead, and copy from that.
    proto_prim = stage.GetPrimAtPath(
        instancer.GetPrototypesRel().GetForwardedTargets()[0]
    )
    list_op = proto_prim.GetMetadata("references")  # Sdf.ReferenceListOp
    items = list_op.explicitItems if list_op.isExplicit else (
        list_op.addedItems or list_op.prependedItems
    )
    ref = items[0]
    # ref.assetPath is relative to whatever layer authored the reference (e.g.
    # a project's out/ directory) -- resolve it against that known root, not
    # against the anonymous session layer you're editing.
    source_layer = Sdf.Layer.FindOrOpen(str(ASSET_ROOT_DIR / ref.assetPath))
    source_path = Sdf.Path.absoluteRootPath.AppendChild(source_layer.defaultPrim)

    num_instances = len(instancer.GetProtoIndicesAttr().Get())

    # Bake as a SIBLING of the instancer, never a child -- deactivating the
    # instancer below must not also deactivate the baked geometry.
    links_scope = UsdGeom.Scope.Define(
        stage, instancer_prim.GetPath().GetParentPath().AppendChild("Baked")
    )
    dest_layer = stage.GetEditTarget().GetLayer()

    xform_ops = []
    for i in range(num_instances):
        dest_path = links_scope.GetPath().AppendChild(f"Instance_{i}")
        # Plain copy, not a reference: copies real geometry, sidesteps the
        # instanceable-prototype opacity problem entirely.
        Sdf.CopySpec(source_layer, source_path, dest_layer, dest_path)
        prim = stage.GetPrimAtPath(dest_path)
        xform_ops.append(UsdGeom.Xformable(prim).AddTransformOp())

    # ComputeInstanceTransformsAtTime returns a Vt.Matrix4dArray, one 4x4
    # matrix per instance, at a given time -- exactly what each baked
    # instance's transform op needs, per frame.
    start, end = stage.GetStartTimeCode(), stage.GetEndTimeCode()
    for frame in range(int(start), int(end) + 1):
        transforms = instancer.ComputeInstanceTransformsAtTime(frame, frame)
        for op, matrix in zip(xform_ops, transforms):
            op.Set(matrix, Usd.TimeCode(frame))

    # Deactivate, don't just hide, the original instancer once its data has
    # been extracted -- see "visibility vs active" below.
    instancer_prim.SetActive(False)
```

Do the baking on an in-memory stage, never the authored source files:

```python
stage = Usd.Stage.Open(path_to_composed_root_layer)
stage.SetEditTarget(Usd.EditTarget(stage.GetSessionLayer()))
# ... bake_point_instancer(...) for each PointInstancer found via stage.Traverse() ...
flat_layer = stage.Flatten()
flat_layer.Export(output_path)
```

## 3. Visibility vs. Active: hiding leftovers correctly

`UsdGeom.Imageable(...).CreateVisibilityAttr().Set(UsdGeom.Tokens.invisible)` is only a
*hint*. Some consumers -- confirmed with three.js-based tools (usdz-viewer.net) --
ignore it outright and render the prim anyway. If you deactivate-vs-hide a prim in the
wrong order relative to prims nested under it, you can also silently delete geometry you
meant to keep.

- To make a prim invisible to *every* consumer, compliant or not: `prim.SetActive(False)`.
  Inactive prims (and everything nested under them) are excluded from composition
  entirely -- no traversal can see them.
- Corollary: never nest geometry you want to keep underneath a prim you are about to
  deactivate. Author replacement/baked geometry as a *sibling*, not a child, of whatever
  you're suppressing.
- Symptom of getting this wrong: a small, untransformed, orphaned mesh sitting at the
  local origin in the exported scene, visible in some viewers (three.js-based ones) but
  not others (Blender's native importer, spec-compliant viewers) -- that's leftover
  prototype/source geometry that was hidden instead of excluded from composition.

## 4. Known third-party bugs (found in this session, not this project's code)

**usd2gltf 0.3.5** (`pip install usd2gltf`):

- Crashes on *any* `PointInstancer` prim in the stage, even one that's inactive/hidden:
  `NameError: name 'point_instancers' is not defined` in `converter.py`'s `process()`.
  The variable is referenced (`point_instancers.append(pi)`) but never initialized.
  One-line local patch: add `point_instancers = []` and
  `point_instancer_prototypes = []` right before the prim-gathering loop (search for
  `point_instancers.append` in the installed `usd2gltf/converter.py`). Upstream bug, not
  something to work around in your own USD authoring -- either bake PointInstancers out
  first (section 2) or patch the installed file.
- Also crashes converting a `UsdGeom.Mesh` whose `normals` attribute is authored but
  empty (0-length array): `ValueError: cannot reshape array of size 0 into shape (0)` in
  `usd2gltf/converters/usd_mesh.py`'s mesh conversion. Not yet fixed as of this writing --
  found but deprioritized in favor of the native-USD-import path.
- Pulls in its own `usd-core` pip dependency (a separate USD build). Run it with plain
  `python`, not a custom `PYTHONPATH` pointed at a different USD distro's `pxr` -- mixing
  the two risks ABI/DLL conflicts.

**usdz-viewer.net / three.js-based viewers and their "download as glTF/GLB" exports:**

- Export whatever static pose is on screen -- **no time-sampled/USD animation survives**
  the round trip, regardless of what the source file contains.
- The downloaded file may claim to be `.glb` (binary glTF) but actually be plain-text
  glTF JSON (starts with `{"asset":...}`, not the 4-byte `glTF` binary magic) with a
  self-embedded base64 data-URI buffer. Most loaders (Blender's glTF importer included)
  tolerate this via content-sniffing, but it is not a spec-conformant `.glb`. Rename to
  `.gltf` if you need it to be honest about its own format.

## 5. Headless Blender as a diagnostic tool

When you don't have GUI access (or want a repeatable check), drive Blender's Python API
directly instead of guessing why an import looks wrong:

```
blender.exe --background --python script.py
```

Inside `script.py`, useful diagnostics that found the actual root causes in this session:

- List every imported object/type: `[(o.name, o.type) for o in bpy.data.objects]` --
  reveals when instanced geometry imported as an empty `POINTCLOUD` with no visible mesh.
- Inspect a geometry-nodes modifier's wiring directly, e.g. whether a "Collection Info"
  node actually points at a populated collection:
  ```python
  for n in modifier.node_group.nodes:
      if n.bl_idname == 'GeometryNodeCollectionInfo':
          print(n.inputs['Collection'].default_value)  # None => broken wiring
  ```
- Confirm baked animation actually varies over time (not just present):
  ```python
  scene.frame_set(1); loc1 = obj.matrix_world.translation.copy()
  scene.frame_set(50); loc50 = obj.matrix_world.translation.copy()
  assert loc1 != loc50
  ```

## 6. `primvars:displayColor` alone doesn't show in Blender -- and implicit
   Gprim primitives (Cube/Cylinder/Sphere/Cone) are a second, separate trap

Symptom: a USD file where every part only has `primvars:displayColor` (no
`UsdShade.Material`) imports into Blender as uniform gray, even though other
viewers (usdview, three.js-based tools like usdz-viewer.net) render the colors
fine directly from `displayColor`.

Root cause: Blender's USD importer *does* read `displayColor` -- it lands as a
mesh color attribute (`mesh.color_attributes` contains `"displayColor"`,
confirmable via `read_mesh_colors` import option, on by default) -- but it does
NOT synthesize a material from it. With zero materials on the object, Solid/
Material-Preview/Rendered viewport shading all fall back to flat gray. No
`usd_import` option (`import_materials`, `import_usd_preview`, `mtl_purpose`,
etc.) changes this -- it isn't a missed flag, Blender just never wires a bare
displayColor primvar to anything shaded.

Fix: author a real `UsdShade.Material` with a `UsdPreviewSurface` shader per
color, bind it with `UsdShade.MaterialBindingAPI.Apply(prim).Bind(material)`
(note `.Apply(prim)`, not just `UsdShade.MaterialBindingAPI(prim)` -- the
latter authors the binding relationship but not the required `apiSchemas`
metadata entry, which `usdchecker`'s `MaterialBindingAPIAppliedChecker` flags).
This repo's `pipeline/usd_utils.py` (`get_material()` / `set_color()`) already
does this, caching one material per (stage, color) pair and reusing it across
prims.

**But this alone is not enough** if the colored prims are implicit Gprim
primitives (`UsdGeom.Cube`, `UsdGeom.Cylinder`, `Sphere`, `Cone`) rather than
explicit `UsdGeom.Mesh`. Confirmed with a minimal isolated test file (one
`Cube`, one triangle `Mesh`, identical material binding on both, nothing else
in the stage): Blender 5.2's importer drops the material on the `Cube` and
keeps it on the `Mesh`, with zero import-option combination changing that. The
USD file is completely correct (verify independently with
`UsdShade.MaterialBindingAPI(prim).ComputeBoundMaterial()`, outside Blender,
before assuming otherwise) -- this is purely a Blender-importer gap for
implicit-primitive material bindings.

Fix (only needed if colors must show in Blender specifically): replace every
`UsdGeom.Cube`/`UsdGeom.Cylinder` with an explicitly tessellated `UsdGeom.Mesh`
carrying real points/faces. `pipeline/usd_utils.py`'s `make_box_mesh()` /
`make_cylinder_mesh()` already do this (one normal per face via `Gf.Cross` of
the first two edges, `SetNormalsInterpolation(uniform)`, plus
`CreateDoubleSidedAttr(True)` so inconsistent winding still renders) -- prefer
those over the implicit `UsdGeom` shape classes for any part that needs a
material to show in Blender or similar tools. `sides=16` (the default in
`make_cylinder_mesh`) reads as reasonably round at small-prop scale while
staying flat-shaded/low-poly; raise it for parts large enough in frame for
facets to read as angular rather than round. Before converting existing code,
grep for reliance on the replaced prim's *type* specifically (e.g.
`GetRadiusAttr()`/`GetAxisAttr()` calls, `UsdGeom.Cylinder(prim)` casts) --
callers that only use the prim's *path* and `XformCommonAPI`/`Xformable`
(translate/rotate) are unaffected by swapping Cylinder/Cube for Mesh, since
both are equally `UsdGeomXformable`.

## 7. USD environment on Windows

If a project's own scripts assume `from pxr import ...` "just works" with the system
`python`, it usually doesn't on Windows without deliberate setup -- see this repo's
`environment.yml` and `CLAUDE.md` for the conda-based setup this template uses (the
PyPI `usd-core` wheel lacks `usdchecker`/`usdview`). If instead working against an
NVIDIA `usd_root`-style binary distro on a given machine:

- The system/PATH `python` typically lacks `pxr` entirely, or has a `pxr` build with a
  mismatched Python ABI (`DLL load failed while importing _tf`).
- Use the bundled interpreter instead (e.g. `usd_root/python/python.exe`).
- Required env vars (mirrors `usd_root/scripts/set_usd_env.bat` /
  `set_usd_python_env.bat`), in PowerShell:
  ```powershell
  $env:USD_INSTALL_DIR = "<path>\usd_root"
  $env:PATH = "$env:USD_INSTALL_DIR\lib;$env:USD_INSTALL_DIR\plugin\usd;$env:USD_INSTALL_DIR\bin;$env:USD_INSTALL_DIR\python;$env:PATH"
  $env:PYTHONPATH = "$env:USD_INSTALL_DIR\lib\python;$env:PYTHONPATH"
  ```
- CLI tools (`usdcat`, `usdchecker`, `usdtree`, `usdzip`) live under `usd_root\bin` and
  are wrapped by `.bat` scripts in `usd_root\scripts\` that set this same environment --
  prefer invoking those wrappers (via `cmd //c`) over calling the `.exe` directly from
  Bash/git-bash, since git-bash's unix-style `PATH`/`PYTHONPATH` values don't reliably
  translate for native Windows executables and DLL search paths.
