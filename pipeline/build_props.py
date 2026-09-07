"""Prop kit build script (asset-roadmap.md §1.5, Phase 2 Task 3): signage,
wreckage (this pipeline's first `UsdVariantSets` use), a static
barricade/checkpoint booth pair (hinge deferred to Phase 5), and a small
clutter kit reusing Task 1's cargo container shell geometry.
"""
from pathlib import Path

from pxr import Gf, UsdGeom

import cargo_utils
from export_utils import export_gltf, export_usdz
from usd_utils import asset_output_paths, create_asset_stage, make_box_mesh, make_cylinder_mesh, set_color

ROOT = Path(__file__).resolve().parent.parent
BUILD_DIR = ROOT / "pipeline" / ".build"
MODELS_DIR = ROOT / "public" / "assets" / "models"


def _new_stage(name):
    build_path = BUILD_DIR / f"prop_{name}.usda"
    if build_path.exists():
        build_path.unlink()
    return create_asset_stage(build_path, "Prop", name)


def _export(stage, name):
    stage.GetRootLayer().Save()
    usdz_path, glb_path = asset_output_paths(MODELS_DIR, "Prop", name)
    export_usdz(stage, usdz_path)
    export_gltf(stage, glb_path)
    print(f"Exported {usdz_path.name}, {glb_path.name}")


# --- Signage kit -------------------------------------------------------

def build_signage(name, board_color, preset=None):
    """A simple post + board sign -- dispatch-board and regional
    graffiti/propaganda flavors differ only by `board_color`/`preset`,
    per the roadmap's no-texture-art-yet note."""
    stage, scopes = _new_stage(name)
    geometry = scopes["Geometry"]

    post = make_cylinder_mesh(stage, geometry.GetPath().AppendChild("Post"), radius=0.04, height=1.2, axis="Y")
    UsdGeom.Xformable(post).AddTranslateOp().Set(Gf.Vec3d(0, 0.6, 0))
    set_color(post.GetPrim(), (0.25, 0.24, 0.22), preset="steel")

    board = make_box_mesh(stage, geometry.GetPath().AppendChild("Board"), (0.5, 0.35, 0.03))
    UsdGeom.Xformable(board).AddTranslateOp().Set(Gf.Vec3d(0, 1.1, 0))
    set_color(board.GetPrim(), board_color, preset)

    _export(stage, name)


# --- Wreckage (first UsdVariantSets use) --------------------------------

def build_wreckage():
    """One asset, one `Condition` variant set on the Geometry scope --
    `Calmed` (a couple of weathered, muted debris pieces) vs `Militarized`
    (more debris plus a charred scorch plate), per §1.3's region-tension
    dressing note. Not two separate assets."""
    stage, scopes = _new_stage("Wreckage")
    geometry = scopes["Geometry"]

    variant_set = geometry.GetVariantSets().AddVariantSet("Condition")
    variant_set.AddVariant("Calmed")
    variant_set.AddVariant("Militarized")

    variant_set.SetVariantSelection("Calmed")
    with variant_set.GetVariantEditContext():
        chunk_a = make_box_mesh(stage, geometry.GetPath().AppendChild("DebrisA"), (0.45, 0.15, 0.3))
        UsdGeom.Xformable(chunk_a).AddTranslateOp().Set(Gf.Vec3d(-0.3, 0.15, 0))
        UsdGeom.Xformable(chunk_a).AddRotateYOp().Set(15.0)
        set_color(chunk_a.GetPrim(), (0.42, 0.36, 0.3), preset="rubber")

        chunk_b = make_box_mesh(stage, geometry.GetPath().AppendChild("DebrisB"), (0.3, 0.1, 0.25))
        UsdGeom.Xformable(chunk_b).AddTranslateOp().Set(Gf.Vec3d(0.35, 0.1, 0.2))
        UsdGeom.Xformable(chunk_b).AddRotateYOp().Set(-25.0)
        set_color(chunk_b.GetPrim(), (0.5, 0.44, 0.36), preset="rubber")

    variant_set.SetVariantSelection("Militarized")
    with variant_set.GetVariantEditContext():
        chunk_a = make_box_mesh(stage, geometry.GetPath().AppendChild("DebrisA"), (0.45, 0.2, 0.3))
        UsdGeom.Xformable(chunk_a).AddTranslateOp().Set(Gf.Vec3d(-0.3, 0.2, 0))
        UsdGeom.Xformable(chunk_a).AddRotateYOp().Set(15.0)
        set_color(chunk_a.GetPrim(), (0.15, 0.14, 0.13), preset="steel")

        chunk_b = make_box_mesh(stage, geometry.GetPath().AppendChild("DebrisB"), (0.3, 0.18, 0.25))
        UsdGeom.Xformable(chunk_b).AddTranslateOp().Set(Gf.Vec3d(0.35, 0.18, 0.2))
        UsdGeom.Xformable(chunk_b).AddRotateYOp().Set(-25.0)
        set_color(chunk_b.GetPrim(), (0.12, 0.11, 0.1), preset="steel")

        scorch = make_box_mesh(stage, geometry.GetPath().AppendChild("ScorchPlate"), (0.6, 0.01, 0.6))
        UsdGeom.Xformable(scorch).AddTranslateOp().Set(Gf.Vec3d(0, 0.01, -0.1))
        set_color(scorch.GetPrim(), (0.05, 0.05, 0.05), preset="unmarked-matte")

    variant_set.SetVariantSelection("Calmed")  # default selection at export time
    _export(stage, "Wreckage")


# --- Barricade / checkpoint booth (static only; hinge deferred to Phase 5) --

def build_barricade():
    """A sawhorse-style static barrier -- no gate-arm/hinge, per this
    prompt's explicit deferral to Phase 5."""
    stage, scopes = _new_stage("Barricade")
    geometry = scopes["Geometry"]

    bar = make_box_mesh(stage, geometry.GetPath().AppendChild("Bar"), (0.9, 0.05, 0.05))
    UsdGeom.Xformable(bar).AddTranslateOp().Set(Gf.Vec3d(0, 0.7, 0))
    set_color(bar.GetPrim(), (0.85, 0.55, 0.1), preset="paint")

    for i, x in enumerate((-0.7, 0.7)):
        leg = make_box_mesh(stage, geometry.GetPath().AppendChild(f"Leg_{i:02d}"), (0.05, 0.35, 0.3))
        UsdGeom.Xformable(leg).AddTranslateOp().Set(Gf.Vec3d(x, 0.35, 0))
        set_color(leg.GetPrim(), (0.2, 0.2, 0.2), preset="steel")

    _export(stage, "Barricade")


def build_checkpoint_booth():
    """A small static guard booth -- box shell + a slightly larger, thin
    peaked-roof cap. Static geometry only."""
    stage, scopes = _new_stage("CheckpointBooth")
    geometry = scopes["Geometry"]

    shell = make_box_mesh(stage, geometry.GetPath().AppendChild("BoothShell"), (0.6, 1.0, 0.6))
    UsdGeom.Xformable(shell).AddTranslateOp().Set(Gf.Vec3d(0, 1.0, 0))
    set_color(shell.GetPrim(), (0.6, 0.55, 0.45), preset="paint")

    roof = make_box_mesh(stage, geometry.GetPath().AppendChild("Roof"), (0.7, 0.06, 0.7))
    UsdGeom.Xformable(roof).AddTranslateOp().Set(Gf.Vec3d(0, 2.06, 0))
    set_color(roof.GetPrim(), (0.25, 0.24, 0.22), preset="steel")

    _export(stage, "CheckpointBooth")


# --- Small clutter kit (reuses Task 1's cargo shell geometry) -----------

def _rehome_to_ground(mesh_prim, half_height):
    """cargo_utils' shell builders sit their shell on top of a pallet
    (translate.y = PALLET_HEIGHT + half_height); reused standalone as
    ground clutter (no pallet underneath), re-home the same shell to sit
    directly on the ground instead of floating at the pallet's height."""
    xformable = UsdGeom.Xformable(mesh_prim)
    op = xformable.GetOrderedXformOps()[0]
    op.Set(Gf.Vec3d(0, half_height, 0))


def build_clutter_barrel():
    """A "damaged"-reading loose barrel -- the same drum shell geometry
    Task 1's ChemicalDrum uses, not new geometry, placed without a pallet."""
    height = 0.95
    stage, scopes = _new_stage("ClutterBarrel")
    shell = cargo_utils.build_drum_shell(stage, scopes, (0.35, 0.32, 0.28), preset="steel", height=height)
    _rehome_to_ground(shell, height / 2)
    _export(stage, "ClutterBarrel")


def build_clutter_crate():
    """A "damaged crate" prop -- literally Task 1's crate shell mesh,
    reused as static dressing rather than re-authored (roadmap §1.5)."""
    size = (0.9, 0.85, 0.9)
    stage, scopes = _new_stage("ClutterCrate")
    shell = cargo_utils.build_crate_shell(stage, scopes, (0.4, 0.32, 0.22), preset=None, size=size)
    _rehome_to_ground(shell, size[1] / 2)
    _export(stage, "ClutterCrate")


def build_props_kit():
    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    build_signage("SignageDispatch", board_color=(0.85, 0.85, 0.9), preset="paint")
    build_signage("SignageGraffiti", board_color=(0.7, 0.2, 0.15), preset=None)
    build_wreckage()
    build_barricade()
    build_checkpoint_booth()
    build_clutter_barrel()
    build_clutter_crate()


if __name__ == "__main__":
    build_props_kit()
