"""Shared, customizable vehicle kit (asset-roadmap.md §1.1; phase3a-shared-
vehicle-kit prompt): a referenceable wheel-corner sub-assembly generator
(Task 2), a detail/greeble kit (Task 3), a hull/cab composition helper built
on `usd_utils.make_profile_extrusion` (Task 4), and door-hinge/cargo-latch
rig helpers (phase3b-mule prompt, Task 1). Nothing here assembles a full
vehicle -- that's Phase 3b (the Mule) and Phase 3c (the Goat), each calling
these same functions with their own parameters.
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
    arch_gap=0.06, arch_thickness=0.04, arch_span_degrees=150.0, arch_segments=10,
    strut_length=0.35, strut_radius=0.035, strut_cap_radius=None, strut_cap_thickness=0.025,
    rim_proud=0.02,
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

    Because the SAME local geometry is referenced un-mirrored at both +X
    and -X wheel positions, the rim can't be offset toward one local-X
    side only (Round 2 second-fix's literal "toward the outboard face"
    framing) -- whichever local side is outboard at one wheel position is
    inboard (and occluded by the tire itself, from the natural outward
    viewing angle) at the other. Instead `rim_proud` makes the rim's own
    axial extent exceed the tire's width, symmetrically, so it protrudes
    past BOTH of the tire's flat faces by that amount -- visible from
    either side regardless of which one ends up outboard when referenced.

    `steerable=True` authors a `_Steer` (rotateY) pivot parenting a `_Spin`
    (rotateX) pivot (front corner); `steerable=False` authors a bare
    `_Spin` pivot only (rear corner) -- both per Phase 1's validated,
    zero-offset two-level pivot chain (roadmap §2.2). The wheel-arch flare
    and suspension strut live in the Geometry scope (not Rig): they're
    positioned relative to the wheel, not the chassis, but don't themselves
    animate.

    `strut_length` has no sensible generic default -- this asset's local
    origin is the wheel's own center, and the strut spans local Y
    `[tire_radius, tire_radius + strut_length]` *before* this corner is
    referenced into a vehicle assembly. Referencing adds another
    `tire_radius` on top (wheels are placed at world `y=tire_radius` so they
    touch the ground), so the strut's world-space top lands at
    `2*tire_radius + strut_length`. Every caller must therefore compute
    `strut_length` from ITS OWN vehicle's wheel-well depth -- the gap
    between the wheel's own top (`2*tire_radius`) and wherever that
    vehicle's body underside actually sits (its chassis deck height) --
    i.e. `strut_length = vehicle_deck_y - 2 * tire_radius`. Leaving the
    default here uncomputed against a real vehicle is exactly the bug this
    parameter used to have: the strut clipped up through the body instead
    of terminating at it. A small disc `StrutMount` cap is authored at the
    strut's top end (using `strut_cap_radius`/`strut_cap_thickness`) so it
    visually terminates against something instead of ending in bare air --
    deliberately NOT tilted/steering-linked, since the same un-mirrored
    asset is referenced at both +X and -X wheel positions (see the rim's
    own `rim_proud` symmetric-fix comment above for why an asymmetric
    feature here would only look right at one of the two positions).

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
        height=tire_width + 2 * rim_proud, axis="X", sides=12,
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

    # Mount-plate cap: terminates the strut against a small disc instead of
    # bare air, so it reads as attaching to something (the chassis mount)
    # rather than a pole poking upward with nothing at its end.
    strut_cap_radius = strut_cap_radius if strut_cap_radius is not None else strut_radius * 2.5
    strut_top_y = tire_radius + strut_length
    strut_cap = make_cylinder_mesh(
        stage, geometry.GetPath().AppendChild("StrutMount"),
        radius=strut_cap_radius, height=strut_cap_thickness, axis="Y",
    )
    UsdGeom.Xformable(strut_cap).AddTranslateOp().Set(
        Gf.Vec3d(0, strut_top_y + strut_cap_thickness / 2.0, 0)
    )
    set_color(strut_cap.GetPrim(), strut_color, preset=strut_preset)

    stage.GetRootLayer().Save()
    usdz_path, glb_path = asset_output_paths(models_dir, "Vehicle", name)
    export_usdz(stage, usdz_path)
    export_gltf(stage, glb_path)
    print(f"Exported {usdz_path.name}, {glb_path.name}")
    return stage, build_path


# --- Task 1 (phase3b): door hinge + cargo latch rig helpers --------------

_VALID_HINGE_AXES = ("X", "Y")


def add_door_hinge(stage, rig_scope, name, hinge_position, door_size, *,
                    door_color=(0.5, 0.5, 0.55), door_preset="paint",
                    hinge_axis="Y"):
    """A `_Hinge` pivot + door panel mesh, hung from its hinge edge -- the
    panel is offset by half its swing dimension from the pivot, so the
    door's FAR edge swings when the pivot rotates, not its hinge edge (the
    classic mistake would be centering the panel on the pivot, which swings
    the door through its own hinge line).

    `hinge_axis` picks which edge is hinged and generalizes the offset math
    to whichever local axis is actually swinging:

    - `"Y"` (default, unchanged from this function's original behavior): a
      vertical hinge line (rotateY), side-swinging barn-style door.
      `hinge_position` is the hinge edge's mount point -- an outer corner
      of the opening -- and the sign of its X component picks which side
      the door is mounted on. The panel is offset by half `door_size[0]`
      (`width`, the swing dimension) back TOWARD the centerline, so a pair
      of doors called at the opening's two outer corners renders CLOSED
      (meeting at X=0) at rest -- the believable default for a review
      render -- and swings outward when the pivot is later rotated open.
    - `"X"`: a horizontal hinge line (rotateX) at the BOTTOM edge of the
      opening, swinging down -- a pickup tailgate. `hinge_position` is that
      bottom edge's mount point. The panel is offset by half `door_size[1]`
      (`height`, the swing dimension here, not width) upward along local Y,
      so it rests upright and closed against the opening above its hinge --
      there's no left/right mirroring to reconcile for a single tailgate,
      unlike the `"Y"` case's two-doors-meeting-at-center convention.

    `door_size` is (width, height, thickness); which of `width`/`height` is
    the "swing dimension" depends on `hinge_axis` as described above.

    Returns (hinge_pivot_prim, door_mesh) -- caller (Task 5, or a future
    vehicle script) poses the pivot open via
    `rig_utils.set_pivot_rotation(hinge, hinge_axis, degrees)`, or leaves it
    at rest for the Babylon runtime to drive at play time.
    """
    if hinge_axis not in _VALID_HINGE_AXES:
        raise ValueError(f"Invalid hinge_axis {hinge_axis!r}; must be one of {_VALID_HINGE_AXES}")

    width, height, thickness = door_size
    hinge = add_pivot_xform(rig_scope, name, "_Hinge", translate=hinge_position)
    door = make_box_mesh(
        stage, hinge.GetPath().AppendChild(f"{name}Door"),
        (width / 2.0, height / 2.0, thickness / 2.0),
    )
    if hinge_axis == "Y":
        side = 1.0 if hinge_position[0] >= 0 else -1.0
        offset = Gf.Vec3d(-side * width / 2.0, 0, 0)
    else:
        offset = Gf.Vec3d(0, height / 2.0, 0)
    UsdGeom.Xformable(door).AddTranslateOp().Set(offset)
    set_color(door.GetPrim(), door_color, preset=door_preset)
    return hinge, door


def add_cargo_latch(stage, rig_scope, name, latch_position, *,
                     latch_size=(0.05, 0.09, 0.03),
                     latch_color=(0.14, 0.14, 0.15), latch_preset="steel"):
    """A `_Latch` pivot (rotateX) + small latch-bar mesh, for the "latching
    cargo bay locks" CLAUDE.md calls out -- deliberately `_Latch`, not
    `_Hinge`: a door hinge carries a large panel through a wide swing (its
    far edge moves a lot), while a latch is a small bar that flips in place
    over the seam it's securing, so the mesh sits at the pivot's own origin
    rather than being offset outward like a door panel.

    `latch_position` is the pivot's mount point (typically straddling a
    cargo bay's door seam) in `rig_scope`'s space; `latch_size` is
    (width, height, thickness) of the latch bar itself.
    """
    lw, lh, lt = latch_size
    latch = add_pivot_xform(rig_scope, name, "_Latch", translate=latch_position)
    bar = make_box_mesh(
        stage, latch.GetPath().AppendChild(f"{name}Bar"),
        (lw / 2.0, lh / 2.0, lt / 2.0),
    )
    set_color(bar.GetPrim(), latch_color, preset=latch_preset)
    return latch, bar


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


def build_roll_bar(stage, parent_scope, name, position, *,
                    half_width, height, bar_radius=0.03,
                    color=(0.15, 0.15, 0.16), preset="steel"):
    """A "goalpost" roll bar: two vertical posts + one horizontal bar
    connecting their tops, all straight `make_cylinder_mesh` segments (no
    bent/curved tube) -- arches over an open cargo bed. `position` is the
    bar's mount point at the bed floor (its two posts rise from there);
    `half_width` is the post spacing (local X), `height` the post height."""
    px, py, pz = position
    for side_name, sign in (("L", -1.0), ("R", 1.0)):
        post = make_cylinder_mesh(
            stage, parent_scope.GetPath().AppendChild(f"{name}Post_{side_name}"),
            radius=bar_radius, height=height, axis="Y",
        )
        UsdGeom.Xformable(post).AddTranslateOp().Set(
            Gf.Vec3d(px + sign * half_width, py + height / 2.0, pz)
        )
        set_color(post.GetPrim(), color, preset=preset)

    crossbar = make_cylinder_mesh(
        stage, parent_scope.GetPath().AppendChild(f"{name}Crossbar"),
        radius=bar_radius, height=2.0 * half_width, axis="X",
    )
    UsdGeom.Xformable(crossbar).AddTranslateOp().Set(Gf.Vec3d(px, py + height, pz))
    set_color(crossbar.GetPrim(), color, preset=preset)
    return crossbar


def build_brush_guard(stage, parent_scope, name, position, *,
                       half_width, height, depth=0.1, bar_radius=0.025,
                       color=(0.12, 0.12, 0.13), preset="steel"):
    """A small tubular frame across the front bumper area: two upright
    posts plus a top and bottom crossbar, all straight cylinder segments
    (same construction philosophy as `build_roll_bar` -- no curved welded
    tube). `position` is the frame's mount point at the bumper; the whole
    frame is offset forward by `depth` so it reads as a standoff guard in
    front of the bumper rather than z-fighting with it."""
    px, py, pz = position
    front_z = pz + depth
    for side_name, sign in (("L", -1.0), ("R", 1.0)):
        post = make_cylinder_mesh(
            stage, parent_scope.GetPath().AppendChild(f"{name}Post_{side_name}"),
            radius=bar_radius, height=height, axis="Y",
        )
        UsdGeom.Xformable(post).AddTranslateOp().Set(
            Gf.Vec3d(px + sign * half_width, py + height / 2.0, front_z)
        )
        set_color(post.GetPrim(), color, preset=preset)

    for bar_name, bar_y in ((f"{name}TopBar", py + height), (f"{name}BottomBar", py)):
        bar = make_cylinder_mesh(
            stage, parent_scope.GetPath().AppendChild(bar_name),
            radius=bar_radius, height=2.0 * half_width, axis="X",
        )
        UsdGeom.Xformable(bar).AddTranslateOp().Set(Gf.Vec3d(px, bar_y, front_z))
        set_color(bar.GetPrim(), color, preset=preset)


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
