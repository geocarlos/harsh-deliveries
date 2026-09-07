"""Shared helpers for exporting an authored OpenUSD scene into the two
artifacts `pipeline/build_assets.py` (and any other asset script) writes to
`public/assets/models/`: a self-contained `.usdz` and a web-runtime-loadable
`.glb`.

Three problems this solves (see the `usd-dcc-export` Claude skill for the
full write-up):

1. `Usd.Stage.CreateNew()` cannot write directly to a `.usdz` path -- USD's
   usdz file format is read-only as a layer format (confirmed: it raises
   "creating package usdz layer is not allowed through this API"). The
   correct way to produce a `.usdz` is to flatten the composed stage into a
   normal layer first, then package *that* with
   `UsdUtils.CreateNewUsdzPackage()`.
2. `UsdGeom.PointInstancer` is unreliably supported outside a full
   Hydra-based renderer -- Blender's importer, `usd2gltf`, and three.js-based
   viewers each handle it differently or skip it entirely, and there is no
   guarantee a given web loader will either. Bake every PointInstancer into
   plain, explicitly time-sampled prims before packaging the final `.usdz`.
3. Neither web engine this template targets reliably *loads* `.usdz` at
   runtime: Babylon.js only added usdz *export* (for iOS AR Quick Look), with
   no USD/usdz import loader at all, and three.js's USD/usdz importer is
   experimental (no proper transform hierarchy in places, no
   skinning/animation). glTF/`.glb` is the best-supported native import
   format for both, so `export_gltf()` converts the flattened stage via
   headless Blender (which already has a mature USD importer) rather than
   relying on either engine to load USD directly. `.usdz` remains the
   pipeline's authoritative/master output for DCC interchange; `.glb` is the
   artifact the web runtime actually loads.
"""
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from pxr import Sdf, Usd, UsdGeom, UsdUtils

_BLENDER_CONVERTER_SCRIPT = Path(__file__).parent / "blender_usd_to_gltf.py"


def _prototype_source(proto_prim, asset_root):
    """A prototype prim marked `instanceable` has its real children hidden
    behind an opaque, unreferenceable internal master prim
    (e.g. `/__Prototype_1`) -- GetChildren() returns [] even though usdtree
    shows children, and you cannot author a new reference targeting the
    master. Recover the plain asset reference the prototype was originally
    authored with instead, and use that as the copy source."""
    list_op = proto_prim.GetMetadata("references")
    items = list_op.explicitItems if list_op.isExplicit else (
        list_op.addedItems or list_op.prependedItems
    )
    ref = items[0]
    layer = Sdf.Layer.FindOrOpen(str(Path(asset_root) / ref.assetPath))
    return layer, Sdf.Path.absoluteRootPath.AppendChild(layer.defaultPrim)


def bake_point_instancer(stage, instancer_prim, asset_root):
    """Replace one PointInstancer with plain, internally-referenced sibling
    prims carrying the same per-instance transforms (time-sampled if the
    instancer's positions/orientations are), then deactivate the original.

    - Copy the source geometry ONCE into a plain template, then
      internal-reference it per instance rather than re-copying the whole
      subtree per instance: a reference remaps relationship targets (e.g.
      each Mesh's material:binding) into every instance's own namespace,
      while a raw copy-per-instance would leave every copy's binding
      pointing at the same original template path.
    - Bake as a SIBLING of the instancer, never a child -- deactivating the
      instancer below must not also deactivate the baked geometry.
    - The template copy itself lives under a dedicated `BakedTemplates`
      scope that gets deactivated once every instance has an internal
      reference into it. Deactivating the *scope* (not the template prim
      each Instance_N references directly) matters: `active` composes
      across reference arcs, so deactivating the template prim itself
      would also deactivate every Instance_N that references it. A
      deactivated ancestor two levels up doesn't reach a prim composed at
      a different namespace path (`Baked/Instance_N`) via a reference arc,
      so this excludes the template from the final scene without taking
      the instances down with it. Skipping this step leaves the template
      as a live, untransformed, undeactivated duplicate of the prototype
      sitting at the origin -- confirmed via an actual Blender/glTF
      export round-trip, not just USD-level inspection (Phase 2 cargo
      stacking validation).
    - Deactivate (`SetActive(False)`), don't just hide, the original
      instancer *and* the external-reference prototype prim it pointed at
      (per Task 0's own required-external-reference convention, that
      prototype is a real, separately-authored prim elsewhere in the
      scene, not a descendant of the instancer -- deactivating the
      instancer alone leaves it as a second undeactivated, untransformed
      duplicate at the origin, distinct from the internal
      `BakedTemplates` copy above). A plain visibility=invisible opinion
      is only a hint that some consumers (e.g. three.js-based tools)
      ignore outright, leaving a leftover, untransformed prototype
      rendered at the origin either way.
    """
    instancer = UsdGeom.PointInstancer(instancer_prim)
    proto_targets = instancer.GetPrototypesRel().GetForwardedTargets()
    proto_prim = stage.GetPrimAtPath(proto_targets[0])
    source_layer, source_path = _prototype_source(proto_prim, asset_root)

    parent_path = instancer_prim.GetPath().GetParentPath()
    dest_layer = stage.GetEditTarget().GetLayer()
    baked_scope = UsdGeom.Scope.Define(stage, parent_path.AppendChild("Baked"))

    templates_scope = UsdGeom.Scope.Define(stage, parent_path.AppendChild("BakedTemplates"))
    template_path = templates_scope.GetPath().AppendChild(proto_prim.GetName())
    Sdf.CopySpec(source_layer, source_path, dest_layer, template_path)

    num_instances = len(instancer.GetProtoIndicesAttr().Get())
    xform_ops = []
    for i in range(num_instances):
        prim = stage.DefinePrim(baked_scope.GetPath().AppendChild(f"Instance_{i}"))
        prim.GetReferences().AddInternalReference(template_path)
        xform_ops.append(UsdGeom.Xformable(prim).AddTransformOp())

    start, end = stage.GetStartTimeCode(), stage.GetEndTimeCode()
    for frame in range(int(start), int(end) + 1):
        transforms = instancer.ComputeInstanceTransformsAtTime(frame, frame)
        for op, matrix in zip(xform_ops, transforms):
            op.Set(matrix, Usd.TimeCode(frame))

    instancer_prim.SetActive(False)
    templates_scope.GetPrim().SetActive(False)
    proto_prim.SetActive(False)


def bake_all_point_instancers(stage, asset_root):
    """Bake every PointInstancer found by traversing `stage`. Edits land on
    the session layer so the authored source files are never touched --
    call this on a stage you're about to export, not the one you saved to
    disk. Returns the number of instancers baked."""
    stage.SetEditTarget(Usd.EditTarget(stage.GetSessionLayer()))
    instancer_prims = [prim for prim in stage.Traverse() if prim.IsA(UsdGeom.PointInstancer)]
    for prim in instancer_prims:
        bake_point_instancer(stage, prim, asset_root)
    return len(instancer_prims)


def export_usdz(stage, output_usdz_path):
    """Flatten `stage`'s full composition (references/variants/payloads)
    into one anonymous layer, then package that as `output_usdz_path`.
    Packaging is a separate step from flattening because
    `Usd.Stage.CreateNew()` refuses to write a `.usdz` layer directly --
    see module docstring."""
    output_usdz_path = Path(output_usdz_path)
    output_usdz_path.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp_dir:
        flat_path = Path(tmp_dir) / (output_usdz_path.stem + ".usdc")
        flat_layer = stage.Flatten()
        flat_layer.Export(str(flat_path))

        if not UsdUtils.CreateNewUsdzPackage(str(flat_path), str(output_usdz_path)):
            raise RuntimeError(f"Failed to package {flat_path} as {output_usdz_path}")

    return output_usdz_path


def _find_blender_executable():
    """Checks the BLENDER_EXECUTABLE env var first, then falls back to
    whatever `blender` resolves to on PATH. Windows doesn't put Blender on
    PATH by default, so BLENDER_EXECUTABLE is usually required there."""
    env_path = os.environ.get("BLENDER_EXECUTABLE")
    if env_path:
        return env_path
    found = shutil.which("blender")
    if found:
        return found
    raise RuntimeError(
        "Could not locate a Blender executable. Set the BLENDER_EXECUTABLE "
        "environment variable to blender.exe's full path, or add it to PATH."
    )


def export_gltf(stage, output_glb_path, blender_executable=None):
    """Flatten `stage` and convert it to a self-contained `.glb` by driving
    headless Blender (`blender_usd_to_gltf.py`) rather than a pure-Python USD
    -> glTF converter: Blender's USD importer already handles
    UsdPreviewSurface materials and real UsdGeom.Mesh geometry (the
    conventions usd_utils.py enforces) more reliably than the alternatives
    (see the usd-dcc-export skill for concrete usd2gltf crash bugs). Runs
    Blender as a subprocess since it's a separate application with its own
    bundled Python, not an importable pxr-side dependency.
    """
    output_glb_path = Path(output_glb_path)
    output_glb_path.parent.mkdir(parents=True, exist_ok=True)
    blender_executable = blender_executable or _find_blender_executable()

    with tempfile.TemporaryDirectory() as tmp_dir:
        flat_path = Path(tmp_dir) / (output_glb_path.stem + ".usdc")
        flat_layer = stage.Flatten()
        flat_layer.Export(str(flat_path))

        result = subprocess.run(
            [
                blender_executable, "--background", "--python", str(_BLENDER_CONVERTER_SCRIPT),
                "--", str(flat_path), str(output_glb_path),
            ],
            capture_output=True, text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"Blender USD->glTF conversion failed (exit {result.returncode}):\n"
                f"{result.stdout}\n{result.stderr}"
            )

    return output_glb_path
