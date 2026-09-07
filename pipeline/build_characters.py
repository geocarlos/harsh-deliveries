"""Placeholder character kit build script (asset-roadmap.md §1.6, Phase 2
Task 4). One placeholder proxy per roster runner: `Geometry` (a single
capsule-style body mesh) + `Hardpoints/Anchor` only -- no `Rig`, no
`Collision`, per §2.1's note that those scopes stay empty until real
character geometry replaces the placeholder.

Placeholder geometry choice: a plain cylinder (via the existing
`make_cylinder_mesh` helper), not a true hemispherical-capped capsule.
`usd_utils.py` has no capsule-mesh helper, and authoring one (tessellated
hemisphere caps) purely for a Phase-6-disposable placeholder isn't worth
the new geometry code -- a flat-capped cylinder reads the same as a capsule
at this silhouette-only, no-texture stage, and every runner uses the same
shape (only `set_color` differs), so the "pick one approach, apply it
consistently" rule is satisfied either way.
"""
from pathlib import Path

from pxr import Gf, UsdGeom

from export_utils import export_gltf, export_usdz
from rig_utils import add_hardpoint
from usd_utils import asset_output_paths, create_asset_stage, make_cylinder_mesh, set_color

ROOT = Path(__file__).resolve().parent.parent
BUILD_DIR = ROOT / "pipeline" / ".build"
MODELS_DIR = ROOT / "public" / "assets" / "models"

BODY_RADIUS = 0.22
BODY_HEIGHT = 1.6

# Six roster runners (docs/game-design/02-character-and-vehicle-design.md
# §2), each a distinct flat placeholder color standing in for portrait art.
ROSTER = [
    ("MaraItoh", (0.15, 0.2, 0.42)),          # navy -- precise, dry "Ledger"
    ("DiegoSalvatierra", (0.55, 0.16, 0.12)),  # warm maroon -- "Padre"
    ("KassFerreira", (0.35, 0.4, 0.22)),       # olive -- ex-military "Kass"
    ("IvetaRusul", (0.42, 0.3, 0.2)),          # earthy brown -- "Highland"
    ("RenOkaforBoyle", (0.85, 0.62, 0.1)),     # bright yellow -- "Wire"
    ("Warden", (0.14, 0.14, 0.15)),            # near-black -- "The Warden"
]


def build_character(name, color):
    build_path = BUILD_DIR / f"character_{name}.usda"
    if build_path.exists():
        build_path.unlink()

    stage, scopes = create_asset_stage(build_path, "Character", name)

    body = make_cylinder_mesh(
        stage, scopes["Geometry"].GetPath().AppendChild("BodyCapsule"),
        radius=BODY_RADIUS, height=BODY_HEIGHT, axis="Y",
    )
    UsdGeom.Xformable(body).AddTranslateOp().Set(Gf.Vec3d(0, BODY_HEIGHT / 2, 0))
    set_color(body.GetPrim(), color, preset="rubber")

    # The single point that aligns to a vehicle's Hardpoints/DriverSeat
    # (or sits at world space on foot, in a future build) -- at the
    # asset's own local origin, i.e. the capsule's feet/base contact
    # point, per roadmap §2.3.
    add_hardpoint(scopes["Hardpoints"], "Anchor", (0, 0, 0))

    stage.GetRootLayer().Save()
    usdz_path, glb_path = asset_output_paths(MODELS_DIR, "Character", name)
    export_usdz(stage, usdz_path)
    export_gltf(stage, glb_path)
    print(f"Exported {usdz_path.name}, {glb_path.name}")


def build_character_kit():
    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    for name, color in ROSTER:
        build_character(name, color)


if __name__ == "__main__":
    build_character_kit()
