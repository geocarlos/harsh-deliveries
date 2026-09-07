"""Cargo container kit (asset-roadmap.md §1.2): a shared pallet base with
standardized tie-down hardpoints, plus one shell-builder function per
container archetype (crate, drum, case, sealed box). Archetypes differ by
silhouette + material only -- cargo doesn't animate on its own, so none of
these author anything into the Rig scope.

`TieDown_01`..`_04` land at the same relative pallet-corner position
regardless of which shell sits on top, since a future loadout-assembly
script matches these by name/count against a vehicle bed's own
`TieDown_NN` hardpoints (roadmap §2.3) -- positional consistency here is
load-bearing, not cosmetic.
"""
from pxr import Gf, UsdGeom

from rig_utils import add_hardpoint
from usd_utils import make_box_mesh, make_cylinder_mesh, set_color

# Pallet footprint -- one source of truth, the same reasoning Phase 4 will
# later apply to its own TILE_LENGTH constant (roadmap §2.6).
PALLET_LENGTH = 1.2  # X
PALLET_WIDTH = 1.0   # Z
PALLET_HEIGHT = 0.15  # Y

TIE_DOWN_INSET = 0.1  # inset from each pallet corner edge

PALLET_COLOR = (0.45, 0.32, 0.18)  # weathered wood-pallet brown


def add_pallet_base(stage, scopes):
    """Authors the pallet base Mesh (Geometry scope) and its four
    `TieDown_NN` hardpoints (Hardpoints scope) at the pallet's corners,
    inset by TIE_DOWN_INSET. Returns the pallet Mesh."""
    geometry, hardpoints = scopes["Geometry"], scopes["Hardpoints"]

    half_extents = (PALLET_LENGTH / 2, PALLET_HEIGHT / 2, PALLET_WIDTH / 2)
    pallet = make_box_mesh(stage, geometry.GetPath().AppendChild("PalletBase"), half_extents)
    UsdGeom.Xformable(pallet).AddTranslateOp().Set(Gf.Vec3d(0, PALLET_HEIGHT / 2, 0))
    set_color(pallet.GetPrim(), PALLET_COLOR, preset="rubber")

    corner_x = PALLET_LENGTH / 2 - TIE_DOWN_INSET
    corner_z = PALLET_WIDTH / 2 - TIE_DOWN_INSET
    corners = {
        "TieDown_01": (corner_x, PALLET_HEIGHT, corner_z),
        "TieDown_02": (-corner_x, PALLET_HEIGHT, corner_z),
        "TieDown_03": (-corner_x, PALLET_HEIGHT, -corner_z),
        "TieDown_04": (corner_x, PALLET_HEIGHT, -corner_z),
    }
    for name, translate in corners.items():
        add_hardpoint(hardpoints, name, translate)

    return pallet


def _place_on_pallet(mesh, half_height):
    """Every shell sits directly on top of the pallet base, not floating or
    embedded in it."""
    UsdGeom.Xformable(mesh).AddTranslateOp().Set(Gf.Vec3d(0, PALLET_HEIGHT + half_height, 0))


def build_crate_shell(stage, scopes, color, preset=None, size=(0.9, 0.85, 0.9)):
    """A box crate shell -- used for both the wood crate and the metal
    parts crate variants, differentiated only by `color`/`preset`."""
    hx, hy, hz = size[0] / 2, size[1] / 2, size[2] / 2
    shell = make_box_mesh(stage, scopes["Geometry"].GetPath().AppendChild("CrateShell"), (hx, hy, hz))
    _place_on_pallet(shell, hy)
    set_color(shell.GetPrim(), color, preset)
    return shell


def build_drum_shell(stage, scopes, color, preset="steel", radius=0.35, height=0.95):
    """A banded steel drum shell, via `make_cylinder_mesh` per this
    prompt's suggested material for volatile chemical drums."""
    shell = make_cylinder_mesh(
        stage, scopes["Geometry"].GetPath().AppendChild("DrumShell"), radius, height, axis="Y",
    )
    _place_on_pallet(shell, height / 2)
    set_color(shell.GetPrim(), color, preset)
    return shell


def build_case_shell(stage, scopes, color, preset="glass-preview", size=(0.9, 0.7, 0.9)):
    """A glass-panel case shell -- a flatter box than the crate archetype,
    reading as a display/transport case rather than a stacked crate."""
    hx, hy, hz = size[0] / 2, size[1] / 2, size[2] / 2
    shell = make_box_mesh(stage, scopes["Geometry"].GetPath().AppendChild("CaseShell"), (hx, hy, hz))
    _place_on_pallet(shell, hy)
    set_color(shell.GetPrim(), color, preset)
    return shell


def build_sealed_box_shell(stage, scopes, color, preset="unmarked-matte", size=(0.85, 0.85, 0.85)):
    """A sealed, unmarked container shell -- a plain box read as
    deliberately featureless (undeclared/illegal cargo)."""
    hx, hy, hz = size[0] / 2, size[1] / 2, size[2] / 2
    shell = make_box_mesh(stage, scopes["Geometry"].GetPath().AppendChild("SealedShell"), (hx, hy, hz))
    _place_on_pallet(shell, hy)
    set_color(shell.GetPrim(), color, preset)
    return shell
