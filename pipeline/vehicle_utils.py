"""Shared, customizable vehicle kit (asset-roadmap.md §1.1; phase3a-shared-
vehicle-kit prompt): a referenceable wheel-corner sub-assembly generator
(Task 2), a detail/greeble kit (Task 3), and a hull/cab composition helper
built on `usd_utils.make_profile_extrusion` (Task 4). Nothing here assembles
a full vehicle -- that's Phase 3b (the Mule) and Phase 3c (the Goat), each
calling these same functions with their own parameters.
"""
import math
from pathlib import Path

from pxr import Gf, UsdGeom

from export_utils import export_gltf, export_usdz
from rig_utils import add_pivot_xform
from usd_utils import (
    asset_output_paths,
    create_asset_stage,
    make_box_mesh,
    make_cylinder_mesh,
    make_frustum_mesh,
    make_profile_extrusion,
    set_color,
)


# --- Task 2: referenceable wheel-corner sub-assembly ---------------------

def _build_wheel_arch(stage, geometry, tire_radius, tire_width, arch_gap,
                       arch_thickness, arch_span_degrees, arch_segments,
                       color, preset):
    """A curved fender-flare shell over the top of the wheel, built with
    `make_profile_extrusion`: a thin arc (outer radius tire_radius+arch_gap+
    arch_thickness, inner radius tire_radius+arch_gap) swept across the
    wheel's own width, instead of a flat box -- a flat box read as an
    unconvincing slab in the superseded attempt's review. Profile: walk the
    outer arc one way, then the inner arc back, closing a thin banana-shaped
    cross-section -- the standard way to build an annular-sector polygon."""
    outer_r = tire_radius + arch_gap + arch_thickness
    inner_r = tire_radius + arch_gap
    start_deg = 90.0 - arch_span_degrees / 2.0
    end_deg = 90.0 + arch_span_degrees / 2.0

    profile = []
    for i in range(arch_segments + 1):
        t = math.radians(start_deg + (end_deg - start_deg) * i / arch_segments)
        profile.append(Gf.Vec2f(outer_r * math.cos(t), outer_r * math.sin(t)))
    for i in reversed(range(arch_segments + 1)):
        t = math.radians(start_deg + (end_deg - start_deg) * i / arch_segments)
        profile.append(Gf.Vec2f(inner_r * math.cos(t), inner_r * math.sin(t)))

    half_width = tire_width / 2.0 + arch_thickness
    arch = make_profile_extrusion(stage, geometry.GetPath().AppendChild("WheelArch"), profile, half_width)
    set_color(arch.GetPrim(), color, preset=preset)
    return arch


def build_wheel_corner(
    build_dir, models_dir, name, *,
    tire_radius, tire_width, rim_radius,
    steerable,
    arch_gap=0.06, arch_thickness=0.04, arch_span_degrees=220.0, arch_segments=10,
    strut_length=0.35, strut_radius=0.035,
    tire_color=(0.04, 0.04, 0.04), tire_preset="rubber",
    rim_color=(0.62, 0.62, 0.65), rim_preset="steel",
    arch_color=(0.16, 0.17, 0.18), arch_preset="paint",
    strut_color=(0.3, 0.32, 0.35), strut_preset="steel",
):
    """Authors and exports one standalone wheel-corner asset (category
    "Vehicle") -- a tire+rim wheel, its wheel-arch flare, and its suspension
    strut, all positioned relative to the wheel's own local origin so the
    SAME asset can be referenced at both +X and -X wheel positions via a
    plain translate override -- no rotation, no mirroring (this prompt's
    Task 2 mirror-symmetric design constraint; a mirror flips face winding/
    normal direction, a rotation doesn't).

    `steerable=True` authors a `_Steer` (rotateY) pivot parenting a `_Spin`
    (rotateX) pivot (front corner); `steerable=False` authors a bare
    `_Spin` pivot only (rear corner) -- both per Phase 1's validated,
    zero-offset two-level pivot chain (roadmap §2.2). The wheel-arch flare
    and suspension strut live in the Geometry scope (not Rig): they're
    positioned relative to the wheel, not the chassis, but don't themselves
    animate.

    Returns (stage, build_path) -- `build_path` is the standalone .usda on
    disk, meant to be referenced into a vehicle assembly (Phase 3b/3c) at
    each of the vehicle's four wheel positions; the .usdz/.glb pair is also
    exported here so the corner is independently viewable/testable on its
    own, the actual point of building it as a real sub-asset.
    """
    build_dir = Path(build_dir)
    build_path = build_dir / f"vehicle_{name.lower()}.usda"
    if build_path.exists():
        build_path.unlink()

    stage, scopes = create_asset_stage(build_path, "Vehicle", name)
    rig, geometry = scopes["Rig"], scopes["Geometry"]

    if steerable:
        steer_pivot = add_pivot_xform(rig, "Wheel", "_Steer")
        spin_pivot = add_pivot_xform(steer_pivot, "Wheel", "_Spin")
    else:
        spin_pivot = add_pivot_xform(rig, "Wheel", "_Spin")

    tire = make_cylinder_mesh(
        stage, spin_pivot.GetPath().AppendChild("Tire"),
        radius=tire_radius, height=tire_width, axis="X",
    )
    set_color(tire.GetPrim(), tire_color, preset=tire_preset)

    rim = make_frustum_mesh(
        stage, spin_pivot.GetPath().AppendChild("Rim"),
        bottom_radius=rim_radius * 0.85, top_radius=rim_radius,
        height=tire_width * 0.7, axis="X", sides=12,
    )
    set_color(rim.GetPrim(), rim_color, preset=rim_preset)

    _build_wheel_arch(
        stage, geometry, tire_radius, tire_width, arch_gap, arch_thickness,
        arch_span_degrees, arch_segments, arch_color, arch_preset,
    )

    strut = make_cylinder_mesh(
        stage, geometry.GetPath().AppendChild("Strut"),
        radius=strut_radius, height=strut_length, axis="Y",
    )
    UsdGeom.Xformable(strut).AddTranslateOp().Set(
        Gf.Vec3d(0, tire_radius + strut_length / 2.0, 0)
    )
    set_color(strut.GetPrim(), strut_color, preset=strut_preset)

    stage.GetRootLayer().Save()
    usdz_path, glb_path = asset_output_paths(models_dir, "Vehicle", name)
    export_usdz(stage, usdz_path)
    export_gltf(stage, glb_path)
    print(f"Exported {usdz_path.name}, {glb_path.name}")
    return stage, build_path


# --- Task 3: detail/greeble kit -------------------------------------------

def build_headlight(stage, parent_scope, name, position, *,
                     housing_size=(0.09, 0.07, 0.04), lens_radius=0.05, lens_depth=0.015,
                     housing_color=(0.08, 0.08, 0.09), lens_color=(0.85, 0.78, 0.5)):
    """Housing box + lens cylinder pair, matching the reference tank's
    two-part headlight pattern -- `position` is the housing's mount point
    on the body, the lens is placed just in front of it along local +Z."""
    hx, hy, hz = (s / 2.0 for s in housing_size)
    housing = make_box_mesh(stage, parent_scope.GetPath().AppendChild(f"{name}Housing"), (hx, hy, hz))
    UsdGeom.Xformable(housing).AddTranslateOp().Set(Gf.Vec3d(*position))
    set_color(housing.GetPrim(), housing_color, preset="steel")

    lens = make_cylinder_mesh(
        stage, parent_scope.GetPath().AppendChild(f"{name}Lens"),
        radius=lens_radius, height=lens_depth, axis="Z",
    )
    UsdGeom.Xformable(lens).AddTranslateOp().Set(
        Gf.Vec3d(position[0], position[1], position[2] + hz + lens_depth / 2.0)
    )
    set_color(lens.GetPrim(), lens_color, preset="glass-preview")
    return housing, lens


def build_mirror(stage, parent_scope, name, position, *,
                  arm_length=0.12, arm_radius=0.012, head_size=(0.03, 0.08, 0.14),
                  color=(0.1, 0.1, 0.11)):
    """A door-mirror stalk (thin cylinder arm) + flat mirror head box,
    mounted at `position` and extending outward along local X -- the sign
    of `position`'s X component picks which side it points toward, so the
    same call works for either side of the vehicle."""
    side = 1.0 if position[0] >= 0 else -1.0

    arm = make_cylinder_mesh(stage, parent_scope.GetPath().AppendChild(f"{name}Arm"),
                              radius=arm_radius, height=arm_length, axis="X")
    UsdGeom.Xformable(arm).AddTranslateOp().Set(
        Gf.Vec3d(position[0] + side * arm_length / 2.0, position[1], position[2])
    )
    set_color(arm.GetPrim(), color, preset="paint")

    hx, hy, hz = (s / 2.0 for s in head_size)
    head = make_box_mesh(stage, parent_scope.GetPath().AppendChild(f"{name}Head"), (hx, hy, hz))
    UsdGeom.Xformable(head).AddTranslateOp().Set(
        Gf.Vec3d(position[0] + side * (arm_length + hx * 0.6), position[1], position[2])
    )
    set_color(head.GetPrim(), color, preset="paint")
    return arm, head


def build_bumper(stage, parent_scope, name, position, *, half_width, height=0.12, depth=0.1,
                  color=(0.12, 0.12, 0.13), preset="paint"):
    """A bumper bar spanning `half_width` across the vehicle's width,
    mounted at `position` (a front or rear bumper mount center)."""
    bumper = make_box_mesh(stage, parent_scope.GetPath().AppendChild(name), (half_width, height / 2.0, depth / 2.0))
    UsdGeom.Xformable(bumper).AddTranslateOp().Set(Gf.Vec3d(*position))
    set_color(bumper.GetPrim(), color, preset=preset)
    return bumper


def build_window_band(stage, parent_scope, name, position, *, half_width, band_height=0.22,
                       depth=0.02, color=(0.12, 0.16, 0.22)):
    """A glass window band sized as an absolute `band_height`, not a
    fraction of the cab's full height -- the superseded attempt's specific
    mistake was a window panel sized as a fraction of its parent volume's
    full height, which read as a solid dark wall slab rather than a window.
    A real vehicle window band is a small strip near the cab's upper
    portion, not most of the cab face."""
    window = make_box_mesh(stage, parent_scope.GetPath().AppendChild(name), (half_width, band_height / 2.0, depth / 2.0))
    UsdGeom.Xformable(window).AddTranslateOp().Set(Gf.Vec3d(*position))
    set_color(window.GetPrim(), color, preset="glass-preview")
    return window


# --- Task 4: hull/cab composition using profile extrusion -----------------

def build_hull_section(stage, parent_scope, name, profile_points, half_width, position,
                        color, preset="paint"):
    """A profile-extruded hull/cab section (hood slope, windshield wedge,
    cab box...) -- positions and colors the result of
    `usd_utils.make_profile_extrusion`, so Phase 3b/3c each supply their own
    profile points (a van's hood slope differs from a pickup's) without
    re-deriving the extrusion call and placement every time."""
    section = make_profile_extrusion(stage, parent_scope.GetPath().AppendChild(name), profile_points, half_width)
    UsdGeom.Xformable(section).AddTranslateOp().Set(Gf.Vec3d(*position))
    set_color(section.GetPrim(), color, preset=preset)
    return section
