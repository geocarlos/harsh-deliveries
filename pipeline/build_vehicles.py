"""Vehicle roster build script (asset-roadmap.md §1.1; phase3b-mule prompt).
Assembles roster vehicles from `vehicle_utils`' shared kit -- the
referenceable wheel-corner sub-assembly, the detail/greeble kit, and the
profile-extruded hull/cab composition helper. Phase 3b builds the Mule (this
file); Phase 3c (a separate prompt) will add the Goat here too, parameterized
differently from the exact same kit, as the proof it generalizes.
"""
import math
from pathlib import Path

from pxr import Gf, UsdGeom

import cargo_utils
import vehicle_utils
from export_utils import export_gltf, export_usdz
from rig_utils import add_hardpoint
from usd_utils import asset_output_paths, create_asset_stage, make_box_mesh, set_color

ROOT = Path(__file__).resolve().parent.parent
BUILD_DIR = ROOT / "pipeline" / ".build"
MODELS_DIR = ROOT / "public" / "assets" / "models"

# --- Mule proportions (adapted from the discarded box-only v4 prototype,
# pipeline/.build/_review/mule_v4_prototype.usda -- its wheel positions,
# ride height, and overall cab/cargo-box lengths are reused as a validated
# starting point; only the construction technique changes) -----------------

MULE_TIRE_RADIUS = 0.36
MULE_TIRE_WIDTH = 0.22
MULE_RIM_RADIUS = 0.22

MULE_TRACK_X = 0.92           # +/-X wheel-center offset from centerline
MULE_FRONT_WHEEL_Z = 1.55
MULE_REAR_WHEEL_Z = -1.35

MULE_DECK_Y = 0.92             # chassis deck / hood-base height
# Strut spans the wheel-well depth: the gap between the wheel's own top
# (2*tire_radius in world space) and the chassis deck it needs to terminate
# against -- see build_wheel_corner's docstring for the full derivation of
# why a generic default strut_length clips through the body instead.
MULE_STRUT_LENGTH = MULE_DECK_Y - 2 * MULE_TIRE_RADIUS
MULE_HOOD_TOP_Y = 1.42
MULE_ROOF_Y = 2.35
MULE_HOOD_FRONT_Z = 2.35        # front bumper line
MULE_WINDSHIELD_BASE_Z = 1.75   # where the hood's flat top meets the slope
MULE_CAB_FRONT_Z = 1.35         # profile's closing face / cab box front

MULE_CAB_HALF_WIDTH = 0.85

# The cargo box's front face overlaps 0.05m into the greenhouse's rear face
# (GREENHOUSE_REAR_Z below) rather than merely touching it -- a hairline gap
# from float rounding would otherwise show as a see-through hole between cab
# and box (confirmed by an actual render: the first pass here left this as a
# separate thin RoofBridge/SillBridge trim over an open gap, which read as a
# hollow void when rendered, not the solid van body a real Mule needs).
GREENHOUSE_HALF_DEPTH = 0.5
GREENHOUSE_REAR_Z = MULE_CAB_FRONT_Z - 2 * GREENHOUSE_HALF_DEPTH
MULE_CARGO_BOX_HALF = (0.93, 0.78, 1.9)   # x, y, z half-extents
MULE_CARGO_BOX_CENTER_Y = MULE_ROOF_Y - MULE_CARGO_BOX_HALF[1]
_cargo_box_front_z = GREENHOUSE_REAR_Z + 0.05
MULE_CARGO_BOX_CENTER_Z = _cargo_box_front_z - MULE_CARGO_BOX_HALF[2]

MULE_PAINT_COLOR = (0.58, 0.58, 0.62)
MULE_ROCKER_COLOR = (0.38, 0.38, 0.41)
MULE_GLASS_COLOR = (0.09, 0.13, 0.18)
MULE_TRIM_COLOR = (0.13, 0.13, 0.14)

# --- Goat proportions (phase3c-goat-reuse-proof): a genuinely different
# pickup anatomy from the same shared kit -- larger off-road tires, a
# lifted stance (longer strut travel, computed the same
# wheel-well-depth way as the Mule's, per Task 1), a shorter single cab
# (no tall van greenhouse), and an open bed instead of an enclosed box. ---

GOAT_TIRE_RADIUS = 0.42        # larger, knobby off-road tire vs. the Mule's 0.36 road tire
GOAT_TIRE_WIDTH = 0.30
GOAT_RIM_RADIUS = 0.24

GOAT_TRACK_X = 0.95             # wider stance than the Mule's 0.92
GOAT_FRONT_WHEEL_Z = 1.35
GOAT_REAR_WHEEL_Z = -1.15       # sits under the open bed, like a real pickup's rear axle

GOAT_DECK_Y = 1.15              # raised chassis deck -- the lifted stance itself
GOAT_STRUT_LENGTH = GOAT_DECK_Y - 2 * GOAT_TIRE_RADIUS  # 0.31, longer travel than the Mule's 0.20

GOAT_HOOD_TOP_Y = 1.62
GOAT_ROOF_Y = 2.05               # lower roof than the Mule's van-height 2.35 -- short pickup cab
GOAT_HOOD_FRONT_Z = 2.05         # front bumper line
GOAT_WINDSHIELD_BASE_Z = 1.55
GOAT_CAB_FRONT_Z = 1.15          # windshield/cab box front

GOAT_CAB_HALF_WIDTH = 0.9
GOAT_CAB_HALF_DEPTH = 0.45       # short single cab, not a long van body
GOAT_CAB_REAR_Z = GOAT_CAB_FRONT_Z - 2 * GOAT_CAB_HALF_DEPTH

# Open bed sits behind the cab with a real gap (unlike the Mule's cargo box,
# which merges flush into the greenhouse) -- a pickup's bed and cab are two
# distinct volumes, not one continuous body.
GOAT_BED_GAP = 0.1
GOAT_BED_FRONT_Z = GOAT_CAB_REAR_Z - GOAT_BED_GAP
GOAT_BED_HALF_Z = 0.9             # 1.8m open bed length
GOAT_BED_CENTER_Z = GOAT_BED_FRONT_Z - GOAT_BED_HALF_Z
GOAT_BED_HALF_X = GOAT_CAB_HALF_WIDTH + 0.05

GOAT_BED_FLOOR_HALF_Y = 0.04
GOAT_BED_FLOOR_CENTER_Y = GOAT_DECK_Y
GOAT_BED_FLOOR_TOP_Y = GOAT_BED_FLOOR_CENTER_Y + GOAT_BED_FLOOR_HALF_Y

GOAT_RAIL_HEIGHT = 0.25
GOAT_RAIL_THICKNESS = 0.06

GOAT_PAINT_COLOR = (0.42, 0.46, 0.32)    # olive/desert-tan, distinct from the Mule's grey
GOAT_ROCKER_COLOR = (0.22, 0.23, 0.20)
GOAT_GLASS_COLOR = (0.09, 0.13, 0.18)
GOAT_TRIM_COLOR = (0.13, 0.13, 0.14)
GOAT_BED_COLOR = (0.15, 0.15, 0.16)       # matte bedliner-style floor/rails


def _reference_wheel_corner(stage, rig_scope, corner_name, source_build_path, position):
    """References a standalone wheel-corner asset (Task 2) into the
    vehicle's own Rig scope via a plain translate-only override -- no
    rotation, no mirroring, per Phase 3a's mirror-symmetric corner design
    (Task 4). Nested under the vehicle's own Rig scope, not a new top-level
    scope, so the vehicle's own top-level structure still matches the exact
    five-scope skeleton even though the referenced asset brings its own
    nested Geometry/Rig/Hardpoints/Collision/Materials subtree one level
    down."""
    xform = UsdGeom.Xform.Define(stage, rig_scope.GetPath().AppendChild(corner_name))
    xform.GetPrim().GetReferences().AddReference(str(Path(source_build_path).resolve()))
    xform.AddTranslateOp().Set(Gf.Vec3d(*position))
    return xform.GetPrim()


def build_mule():
    name = "Mule"
    build_path = BUILD_DIR / "vehicle_mule.usda"
    if build_path.exists():
        build_path.unlink()

    # --- Task 2: the Mule's two wheel corners (standalone sub-assets) ----
    _, front_corner_path = vehicle_utils.build_wheel_corner(
        BUILD_DIR, MODELS_DIR, "MuleFrontCorner",
        tire_radius=MULE_TIRE_RADIUS, tire_width=MULE_TIRE_WIDTH,
        rim_radius=MULE_RIM_RADIUS, steerable=True,
        strut_length=MULE_STRUT_LENGTH,
    )
    _, rear_corner_path = vehicle_utils.build_wheel_corner(
        BUILD_DIR, MODELS_DIR, "MuleRearCorner",
        tire_radius=MULE_TIRE_RADIUS, tire_width=MULE_TIRE_WIDTH,
        rim_radius=MULE_RIM_RADIUS, steerable=False,
        strut_length=MULE_STRUT_LENGTH,
    )

    stage, scopes = create_asset_stage(build_path, "Vehicle", name)
    geometry, rig = scopes["Geometry"], scopes["Rig"]
    hardpoints, collision = scopes["Hardpoints"], scopes["Collision"]

    # --- Task 3: hood-into-windshield profile-extruded panel -------------
    hood_windshield_profile = [
        Gf.Vec2f(MULE_CAB_FRONT_Z, MULE_DECK_Y),           # bottom-rear
        Gf.Vec2f(MULE_HOOD_FRONT_Z, MULE_DECK_Y),           # bottom-front
        Gf.Vec2f(MULE_HOOD_FRONT_Z, MULE_HOOD_TOP_Y),       # hood's flat top, front
        Gf.Vec2f(MULE_WINDSHIELD_BASE_Z, MULE_HOOD_TOP_Y),  # hood meets windshield base
        Gf.Vec2f(MULE_CAB_FRONT_Z, MULE_ROOF_Y),            # top of windshield / roofline
    ]
    vehicle_utils.build_hull_section(
        stage, geometry, "HoodWindshield", hood_windshield_profile,
        MULE_CAB_HALF_WIDTH, position=(0, 0, 0),
        color=MULE_PAINT_COLOR, preset="paint",
    )

    # A thin glass insert on the windshield's own sloped face -- the profile
    # panel above is the body's sheet-metal/frame shape (one continuous
    # surface, per Task 3), but a van still needs visibly transparent glass
    # where the windshield actually is, or the cab reads as solid metal with
    # no window at all (caught by rendering and looking: the merged panel
    # alone was indistinguishable from the hood). Rotated to match the
    # windshield segment's own slope (`windshield_base_z, hood_top_y` up to
    # `cab_front_z, roof_y`) and offset outward along that segment's normal
    # by a hair so it doesn't z-fight the coplanar body panel underneath.
    windshield_dz = MULE_CAB_FRONT_Z - MULE_WINDSHIELD_BASE_Z
    windshield_dy = MULE_ROOF_Y - MULE_HOOD_TOP_Y
    windshield_len = math.hypot(windshield_dz, windshield_dy)
    windshield_angle_deg = math.degrees(math.atan2(windshield_dz, windshield_dy))
    windshield_mid_z = (MULE_WINDSHIELD_BASE_Z + MULE_CAB_FRONT_Z) / 2.0
    windshield_mid_y = (MULE_HOOD_TOP_Y + MULE_ROOF_Y) / 2.0
    outward_z, outward_y = windshield_dy / windshield_len, -windshield_dz / windshield_len
    glass_offset = 0.02
    windshield_glass = make_box_mesh(
        stage, geometry.GetPath().AppendChild("Windshield"),
        (MULE_CAB_HALF_WIDTH * 0.82, windshield_len / 2.0 - 0.03, 0.01),
    )
    UsdGeom.Xformable(windshield_glass).AddTranslateOp().Set(Gf.Vec3d(
        0, windshield_mid_y + outward_y * glass_offset, windshield_mid_z + outward_z * glass_offset,
    ))
    UsdGeom.Xformable(windshield_glass).AddRotateXOp().Set(windshield_angle_deg)
    set_color(windshield_glass.GetPrim(), MULE_GLASS_COLOR, preset="glass-preview")

    # Cab body + greenhouse -- genuinely box-shaped, per Task 3. Both are
    # sized in depth to reach all the way back to the cargo box's front face
    # (no gap, no separate bridging trim -- see the module-level comment on
    # MULE_CARGO_BOX_HALF/_cargo_box_front_z for why: a real van's body is
    # one continuous panel from windshield to rear doors).
    cab_lower_half = (MULE_CAB_HALF_WIDTH, 0.275, (MULE_CAB_FRONT_Z - _cargo_box_front_z) / 2.0)
    cab_lower_z = MULE_CAB_FRONT_Z - cab_lower_half[2]
    cab_lower = make_box_mesh(stage, geometry.GetPath().AppendChild("CabLower"), cab_lower_half)
    UsdGeom.Xformable(cab_lower).AddTranslateOp().Set(
        Gf.Vec3d(0, MULE_DECK_Y + cab_lower_half[1], cab_lower_z)
    )
    set_color(cab_lower.GetPrim(), MULE_PAINT_COLOR, preset="paint")

    # Width matches CargoBox's (MULE_CARGO_BOX_HALF[0]) exactly, not a
    # narrower taper -- Round 2's review render found the box's front-top
    # corners poking out past a narrower (0.78) greenhouse at this seam,
    # reading as a distracting ledge. CabLower staying narrower than both
    # (0.85) is a separate, smaller step that read fine on review.
    greenhouse_half = (MULE_CARGO_BOX_HALF[0], 0.35, GREENHOUSE_HALF_DEPTH)
    greenhouse_y = MULE_ROOF_Y - greenhouse_half[1]
    greenhouse_z = MULE_CAB_FRONT_Z - greenhouse_half[2]
    greenhouse = make_box_mesh(stage, geometry.GetPath().AppendChild("CabGreenhouse"), greenhouse_half)
    UsdGeom.Xformable(greenhouse).AddTranslateOp().Set(Gf.Vec3d(0, greenhouse_y, greenhouse_z))
    set_color(greenhouse.GetPrim(), MULE_PAINT_COLOR, preset="paint")

    # Side glass -- absolute band height per build_window_band's own
    # convention, sized/positioned as a modest strip in the greenhouse wall.
    side_window_half_x = 0.015
    for side_name, sign in (("L", -1.0), ("R", 1.0)):
        vehicle_utils.build_window_band(
            stage, geometry, f"SideGlass_{side_name}",
            (sign * (greenhouse_half[0] + side_window_half_x), greenhouse_y, greenhouse_z),
            half_width=side_window_half_x, band_height=0.32, depth=0.275,
            color=MULE_GLASS_COLOR,
        )

    # Two-tone rocker panel along both sides (reads as a lower body accent,
    # matching the v4 prototype's validated look).
    rocker_half = (0.97, 0.18, 2.275)
    rocker = make_box_mesh(stage, geometry.GetPath().AppendChild("Rocker"), rocker_half)
    UsdGeom.Xformable(rocker).AddTranslateOp().Set(Gf.Vec3d(0, MULE_DECK_Y - rocker_half[1], 0.05))
    set_color(rocker.GetPrim(), MULE_ROCKER_COLOR, preset="paint")

    # --- Enclosed cargo box (Task 3) --------------------------------------
    cargo_box = make_box_mesh(stage, geometry.GetPath().AppendChild("CargoBox"), MULE_CARGO_BOX_HALF)
    UsdGeom.Xformable(cargo_box).AddTranslateOp().Set(
        Gf.Vec3d(0, MULE_CARGO_BOX_CENTER_Y, MULE_CARGO_BOX_CENTER_Z)
    )
    set_color(cargo_box.GetPrim(), MULE_PAINT_COLOR, preset="paint")

    # TieDown_01..04 -- reuse cargo_utils' own pallet-footprint constants
    # exactly (not new numbers), so any compatible cargo container mounts
    # this bed (roadmap §1.1/§1.7).
    corner_x = cargo_utils.PALLET_LENGTH / 2 - cargo_utils.TIE_DOWN_INSET
    corner_z = cargo_utils.PALLET_WIDTH / 2 - cargo_utils.TIE_DOWN_INSET
    bed_floor_y = MULE_CARGO_BOX_CENTER_Y - MULE_CARGO_BOX_HALF[1]
    tie_downs = {
        "TieDown_01": (corner_x, bed_floor_y, MULE_CARGO_BOX_CENTER_Z + corner_z),
        "TieDown_02": (-corner_x, bed_floor_y, MULE_CARGO_BOX_CENTER_Z + corner_z),
        "TieDown_03": (-corner_x, bed_floor_y, MULE_CARGO_BOX_CENTER_Z - corner_z),
        "TieDown_04": (corner_x, bed_floor_y, MULE_CARGO_BOX_CENTER_Z - corner_z),
    }
    for tie_name, translate in tie_downs.items():
        add_hardpoint(hardpoints, tie_name, translate)

    # --- Task 5: details ---------------------------------------------------
    vehicle_utils.build_bumper(
        stage, geometry, "BumperFront", (0, 0.64, MULE_HOOD_FRONT_Z + 0.11),
        half_width=1.0, height=0.12, depth=0.1,
        color=MULE_TRIM_COLOR, preset="unmarked-matte",
    )
    rear_face_z = MULE_CARGO_BOX_CENTER_Z - MULE_CARGO_BOX_HALF[2]
    vehicle_utils.build_bumper(
        stage, geometry, "BumperRear", (0, 0.64, rear_face_z - 0.1),
        half_width=0.99, height=0.12, depth=0.1,
        color=MULE_TRIM_COLOR, preset="unmarked-matte",
    )

    for side_name, sign in (("L", -1.0), ("R", 1.0)):
        vehicle_utils.build_headlight(
            stage, geometry, f"Headlight_{side_name}",
            (sign * 0.72, 1.05, MULE_HOOD_FRONT_Z),
        )
        vehicle_utils.build_mirror(
            stage, geometry, f"Mirror_{side_name}",
            (sign * cab_lower_half[0], 1.75, cab_lower_z + 0.4),
        )

    # No separate wheel-arch geometry here: each referenced WheelCorner_*
    # (Task 2/4 below) already carries its own curved, profile-extruded
    # fender flare (vehicle_utils._build_wheel_arch) at the wheel's own
    # local origin -- authoring a second, flat-box arch directly on the
    # vehicle turned out to duplicate it with mismatched placement (caught
    # by rendering and looking, per this phase's own acceptance criteria:
    # the box arches floated outside the tire's outer face instead of
    # wrapping it).

    # Rear double barn doors, hinged at the cargo box's two outer top-to-
    # bottom edges -- closed (meeting at X=0) at rest, per add_door_hinge's
    # documented default pose. Offset slightly proud of the box's own rear
    # wall (not coincident with it) so the doors read as applied panels
    # with a visible parting seam, rather than z-fighting with (and being
    # indistinguishable from) the box's own solid rear face.
    door_height = 2.0 * MULE_CARGO_BOX_HALF[1]
    door_center_y = MULE_CARGO_BOX_CENTER_Y
    door_z = rear_face_z - 0.025
    for door_name, x_sign in (("Door_RearL", -1.0), ("Door_RearR", 1.0)):
        vehicle_utils.add_door_hinge(
            stage, rig, door_name,
            (x_sign * MULE_CARGO_BOX_HALF[0], door_center_y, door_z),
            (MULE_CARGO_BOX_HALF[0], door_height, 0.04),
            door_color=MULE_PAINT_COLOR,
        )

    # Cargo latch straddling the two rear doors' meeting seam.
    vehicle_utils.add_cargo_latch(
        stage, rig, "CargoLatch", (0, door_center_y, rear_face_z - 0.03),
    )

    # --- Collision hulls (§2.5, non-negotiable per the roadmap) -----------
    chassis_hull = make_box_mesh(
        stage, collision.GetPath().AppendChild("Hull_Chassis"),
        (MULE_CAB_HALF_WIDTH, 0.5, (MULE_HOOD_FRONT_Z - cab_lower_z - cab_lower_half[2]) / 2.0 + 0.1),
    )
    UsdGeom.Xformable(chassis_hull).AddTranslateOp().Set(
        Gf.Vec3d(0, MULE_DECK_Y, (MULE_HOOD_FRONT_Z + cab_lower_z - cab_lower_half[2]) / 2.0)
    )

    cargo_hull = make_box_mesh(
        stage, collision.GetPath().AppendChild("Hull_CargoBox"), MULE_CARGO_BOX_HALF,
    )
    UsdGeom.Xformable(cargo_hull).AddTranslateOp().Set(
        Gf.Vec3d(0, MULE_CARGO_BOX_CENTER_Y, MULE_CARGO_BOX_CENTER_Z)
    )

    # --- Driver seat / exit point hardpoints (§1.6, §2.3) -----------------
    add_hardpoint(hardpoints, "DriverSeat", (-0.4, MULE_DECK_Y + 0.3, cab_lower_z))
    add_hardpoint(hardpoints, "ExitPoint", (-MULE_CAB_HALF_WIDTH - 0.5, MULE_DECK_Y - 0.3, cab_lower_z))

    # --- Task 4: reference the wheel corners into the assembly ------------
    _reference_wheel_corner(stage, rig, "WheelCorner_FL", front_corner_path,
                             (-MULE_TRACK_X, MULE_TIRE_RADIUS, MULE_FRONT_WHEEL_Z))
    _reference_wheel_corner(stage, rig, "WheelCorner_FR", front_corner_path,
                             (MULE_TRACK_X, MULE_TIRE_RADIUS, MULE_FRONT_WHEEL_Z))
    _reference_wheel_corner(stage, rig, "WheelCorner_RL", rear_corner_path,
                             (-MULE_TRACK_X, MULE_TIRE_RADIUS, MULE_REAR_WHEEL_Z))
    _reference_wheel_corner(stage, rig, "WheelCorner_RR", rear_corner_path,
                             (MULE_TRACK_X, MULE_TIRE_RADIUS, MULE_REAR_WHEEL_Z))

    stage.GetRootLayer().Save()

    usdz_path, glb_path = asset_output_paths(MODELS_DIR, "Vehicle", name)
    export_usdz(stage, usdz_path)
    export_gltf(stage, glb_path)
    print(f"Exported {usdz_path.name}, {glb_path.name}")


def build_goat():
    name = "Goat"
    build_path = BUILD_DIR / "vehicle_goat.usda"
    if build_path.exists():
        build_path.unlink()

    # --- Wheel corners: reuse build_wheel_corner (Task 2) with the Goat's
    # own off-road tire/rim proportions and its own lifted-stance
    # strut_length (Task 1), not the Mule's numbers. --------------------
    _, front_corner_path = vehicle_utils.build_wheel_corner(
        BUILD_DIR, MODELS_DIR, "GoatFrontCorner",
        tire_radius=GOAT_TIRE_RADIUS, tire_width=GOAT_TIRE_WIDTH,
        rim_radius=GOAT_RIM_RADIUS, steerable=True,
        strut_length=GOAT_STRUT_LENGTH,
    )
    _, rear_corner_path = vehicle_utils.build_wheel_corner(
        BUILD_DIR, MODELS_DIR, "GoatRearCorner",
        tire_radius=GOAT_TIRE_RADIUS, tire_width=GOAT_TIRE_WIDTH,
        rim_radius=GOAT_RIM_RADIUS, steerable=False,
        strut_length=GOAT_STRUT_LENGTH,
    )

    stage, scopes = create_asset_stage(build_path, "Vehicle", name)
    geometry, rig = scopes["Geometry"], scopes["Rig"]
    hardpoints, collision = scopes["Hardpoints"], scopes["Collision"]

    # --- Hood-into-windshield profile-extruded panel (Task 3 reuse) -----
    # Same build_hull_section call as the Mule, but with the Goat's own
    # profile points: a shorter hood, a lower roofline -- pickup
    # proportions, not a van's.
    hood_windshield_profile = [
        Gf.Vec2f(GOAT_CAB_FRONT_Z, GOAT_DECK_Y),
        Gf.Vec2f(GOAT_HOOD_FRONT_Z, GOAT_DECK_Y),
        Gf.Vec2f(GOAT_HOOD_FRONT_Z, GOAT_HOOD_TOP_Y),
        Gf.Vec2f(GOAT_WINDSHIELD_BASE_Z, GOAT_HOOD_TOP_Y),
        Gf.Vec2f(GOAT_CAB_FRONT_Z, GOAT_ROOF_Y),
    ]
    vehicle_utils.build_hull_section(
        stage, geometry, "HoodWindshield", hood_windshield_profile,
        GOAT_CAB_HALF_WIDTH, position=(0, 0, 0),
        color=GOAT_PAINT_COLOR, preset="paint",
    )

    # Windshield glass insert, same technique as the Mule's (angled box
    # matching the windshield segment's own slope) with the Goat's values.
    windshield_dz = GOAT_CAB_FRONT_Z - GOAT_WINDSHIELD_BASE_Z
    windshield_dy = GOAT_ROOF_Y - GOAT_HOOD_TOP_Y
    windshield_len = math.hypot(windshield_dz, windshield_dy)
    windshield_angle_deg = math.degrees(math.atan2(windshield_dz, windshield_dy))
    windshield_mid_z = (GOAT_WINDSHIELD_BASE_Z + GOAT_CAB_FRONT_Z) / 2.0
    windshield_mid_y = (GOAT_HOOD_TOP_Y + GOAT_ROOF_Y) / 2.0
    outward_z, outward_y = windshield_dy / windshield_len, -windshield_dz / windshield_len
    glass_offset = 0.02
    windshield_glass = make_box_mesh(
        stage, geometry.GetPath().AppendChild("Windshield"),
        (GOAT_CAB_HALF_WIDTH * 0.82, windshield_len / 2.0 - 0.03, 0.01),
    )
    UsdGeom.Xformable(windshield_glass).AddTranslateOp().Set(Gf.Vec3d(
        0, windshield_mid_y + outward_y * glass_offset, windshield_mid_z + outward_z * glass_offset,
    ))
    UsdGeom.Xformable(windshield_glass).AddRotateXOp().Set(windshield_angle_deg)
    set_color(windshield_glass.GetPrim(), GOAT_GLASS_COLOR, preset="glass-preview")

    # Cab body + greenhouse -- boxes, same reasoning as the Mule's, but
    # short (single-cab depth) with a real gap behind them to the bed,
    # instead of extending all the way back to a cargo box.
    cab_lower_half = (GOAT_CAB_HALF_WIDTH, 0.275, GOAT_CAB_HALF_DEPTH)
    cab_lower_z = GOAT_CAB_FRONT_Z - cab_lower_half[2]
    cab_lower = make_box_mesh(stage, geometry.GetPath().AppendChild("CabLower"), cab_lower_half)
    UsdGeom.Xformable(cab_lower).AddTranslateOp().Set(
        Gf.Vec3d(0, GOAT_DECK_Y + cab_lower_half[1], cab_lower_z)
    )
    set_color(cab_lower.GetPrim(), GOAT_PAINT_COLOR, preset="paint")

    greenhouse_half = (GOAT_CAB_HALF_WIDTH, 0.3, GOAT_CAB_HALF_DEPTH)
    greenhouse_y = GOAT_ROOF_Y - greenhouse_half[1]
    greenhouse_z = GOAT_CAB_FRONT_Z - greenhouse_half[2]
    greenhouse = make_box_mesh(stage, geometry.GetPath().AppendChild("CabGreenhouse"), greenhouse_half)
    UsdGeom.Xformable(greenhouse).AddTranslateOp().Set(Gf.Vec3d(0, greenhouse_y, greenhouse_z))
    set_color(greenhouse.GetPrim(), GOAT_PAINT_COLOR, preset="paint")

    side_window_half_x = 0.015
    for side_name, sign in (("L", -1.0), ("R", 1.0)):
        vehicle_utils.build_window_band(
            stage, geometry, f"SideGlass_{side_name}",
            (sign * (greenhouse_half[0] + side_window_half_x), greenhouse_y, greenhouse_z),
            half_width=side_window_half_x, band_height=0.3, depth=0.5,
            color=GOAT_GLASS_COLOR,
        )

    rocker_half = (GOAT_CAB_HALF_WIDTH + 0.02, 0.15, GOAT_CAB_HALF_DEPTH + 0.05)
    rocker = make_box_mesh(stage, geometry.GetPath().AppendChild("Rocker"), rocker_half)
    UsdGeom.Xformable(rocker).AddTranslateOp().Set(Gf.Vec3d(0, GOAT_DECK_Y - rocker_half[1], cab_lower_z))
    set_color(rocker.GetPrim(), GOAT_ROCKER_COLOR, preset="paint")

    # --- Open bed: a shallow floor pan + low side/front rails, NOT an
    # enclosed box like the Mule's -- this is the Goat's defining
    # silhouette difference. --------------------------------------------
    bed_floor = make_box_mesh(
        stage, geometry.GetPath().AppendChild("BedFloor"),
        (GOAT_BED_HALF_X, GOAT_BED_FLOOR_HALF_Y, GOAT_BED_HALF_Z),
    )
    UsdGeom.Xformable(bed_floor).AddTranslateOp().Set(
        Gf.Vec3d(0, GOAT_BED_FLOOR_CENTER_Y, GOAT_BED_CENTER_Z)
    )
    set_color(bed_floor.GetPrim(), GOAT_BED_COLOR, preset="unmarked-matte")

    rail_half = (GOAT_RAIL_THICKNESS / 2.0, GOAT_RAIL_HEIGHT / 2.0, GOAT_BED_HALF_Z)
    for side_name, sign in (("L", -1.0), ("R", 1.0)):
        rail = make_box_mesh(stage, geometry.GetPath().AppendChild(f"BedRail_{side_name}"), rail_half)
        UsdGeom.Xformable(rail).AddTranslateOp().Set(Gf.Vec3d(
            sign * (GOAT_BED_HALF_X - rail_half[0]), GOAT_BED_FLOOR_TOP_Y + rail_half[1], GOAT_BED_CENTER_Z,
        ))
        set_color(rail.GetPrim(), GOAT_PAINT_COLOR, preset="paint")

    front_rail_half = (GOAT_BED_HALF_X, GOAT_RAIL_HEIGHT / 2.0, GOAT_RAIL_THICKNESS / 2.0)
    front_rail = make_box_mesh(stage, geometry.GetPath().AppendChild("BedRail_Front"), front_rail_half)
    UsdGeom.Xformable(front_rail).AddTranslateOp().Set(Gf.Vec3d(
        0, GOAT_BED_FLOOR_TOP_Y + front_rail_half[1], GOAT_BED_FRONT_Z - front_rail_half[2],
    ))
    set_color(front_rail.GetPrim(), GOAT_PAINT_COLOR, preset="paint")
    # No rear rail: the tailgate (below) closes that edge instead.

    # TieDown_01..04 -- reuse cargo_utils' pallet-footprint constants
    # exactly, same convention as the Mule's enclosed bed.
    corner_x = cargo_utils.PALLET_LENGTH / 2 - cargo_utils.TIE_DOWN_INSET
    corner_z = cargo_utils.PALLET_WIDTH / 2 - cargo_utils.TIE_DOWN_INSET
    tie_downs = {
        "TieDown_01": (corner_x, GOAT_BED_FLOOR_TOP_Y, GOAT_BED_CENTER_Z + corner_z),
        "TieDown_02": (-corner_x, GOAT_BED_FLOOR_TOP_Y, GOAT_BED_CENTER_Z + corner_z),
        "TieDown_03": (-corner_x, GOAT_BED_FLOOR_TOP_Y, GOAT_BED_CENTER_Z - corner_z),
        "TieDown_04": (corner_x, GOAT_BED_FLOOR_TOP_Y, GOAT_BED_CENTER_Z - corner_z),
    }
    for tie_name, translate in tie_downs.items():
        add_hardpoint(hardpoints, tie_name, translate)

    # --- Tailgate (Task 2 reuse): bottom-hinged, swings down, via the same
    # add_door_hinge function the Mule's side-hinged barn doors use, just
    # with hinge_axis="X". -------------------------------------------------
    bed_rear_z = GOAT_BED_CENTER_Z - GOAT_BED_HALF_Z
    tailgate_z = bed_rear_z - 0.025
    tailgate_height = GOAT_RAIL_HEIGHT
    vehicle_utils.add_door_hinge(
        stage, rig, "Tailgate",
        (0, GOAT_BED_FLOOR_TOP_Y, tailgate_z),
        (2.0 * GOAT_BED_HALF_X, tailgate_height, GOAT_RAIL_THICKNESS),
        door_color=GOAT_PAINT_COLOR,
        hinge_axis="X",
    )
    vehicle_utils.add_cargo_latch(
        stage, rig, "TailgateLatch",
        (0, GOAT_BED_FLOOR_TOP_Y + tailgate_height / 2.0, tailgate_z - 0.03),
    )

    # --- Roll bar + brush guard (Task 3 reuse) --------------------------
    # Bare bright steel, not the body paint color -- reads as a raw
    # aftermarket accent against the painted body, and stands out clearly
    # at full-vehicle scale instead of blending into the olive paint.
    GOAT_ACCENT_STEEL = (0.6, 0.61, 0.64)
    vehicle_utils.build_roll_bar(
        stage, geometry, "RollBar",
        position=(0, GOAT_BED_FLOOR_TOP_Y, GOAT_CAB_REAR_Z - 0.05),
        half_width=GOAT_BED_HALF_X - 0.15, height=0.85,
        bar_radius=0.04, color=GOAT_ACCENT_STEEL,
    )
    front_bumper_z = GOAT_HOOD_FRONT_Z + 0.15
    vehicle_utils.build_brush_guard(
        stage, geometry, "BrushGuard",
        position=(0, GOAT_DECK_Y - 0.15, front_bumper_z + 0.06),
        half_width=GOAT_CAB_HALF_WIDTH * 0.5, height=0.32,
        bar_radius=0.03, color=GOAT_ACCENT_STEEL,
    )

    # --- Bumpers, headlights, mirrors (Task 3/4 reuse) ------------------
    vehicle_utils.build_bumper(
        stage, geometry, "BumperFront", (0, GOAT_DECK_Y - 0.28, front_bumper_z),
        half_width=GOAT_CAB_HALF_WIDTH * 0.95, height=0.14, depth=0.12,
        color=GOAT_TRIM_COLOR, preset="unmarked-matte",
    )
    rear_bumper_z = bed_rear_z - 0.15
    vehicle_utils.build_bumper(
        stage, geometry, "BumperRear", (0, GOAT_DECK_Y - 0.28, rear_bumper_z),
        half_width=GOAT_BED_HALF_X * 0.9, height=0.14, depth=0.12,
        color=GOAT_TRIM_COLOR, preset="unmarked-matte",
    )

    for side_name, sign in (("L", -1.0), ("R", 1.0)):
        vehicle_utils.build_headlight(
            stage, geometry, f"Headlight_{side_name}",
            (sign * 0.75, GOAT_DECK_Y + 0.2, GOAT_HOOD_FRONT_Z),
        )
        vehicle_utils.build_mirror(
            stage, geometry, f"Mirror_{side_name}",
            (sign * cab_lower_half[0], GOAT_ROOF_Y - 0.55, cab_lower_z + 0.35),
        )

    # --- Collision hulls (§2.5): chassis + bed, at minimum --------------
    chassis_hull = make_box_mesh(
        stage, collision.GetPath().AppendChild("Hull_Chassis"),
        (GOAT_CAB_HALF_WIDTH, 0.5, (GOAT_HOOD_FRONT_Z - GOAT_CAB_REAR_Z) / 2.0),
    )
    UsdGeom.Xformable(chassis_hull).AddTranslateOp().Set(
        Gf.Vec3d(0, GOAT_DECK_Y, (GOAT_HOOD_FRONT_Z + GOAT_CAB_REAR_Z) / 2.0)
    )

    bed_hull_bottom = GOAT_BED_FLOOR_CENTER_Y - GOAT_BED_FLOOR_HALF_Y
    bed_hull_top = GOAT_BED_FLOOR_TOP_Y + GOAT_RAIL_HEIGHT
    bed_hull_half_y = (bed_hull_top - bed_hull_bottom) / 2.0
    bed_hull_center_y = (bed_hull_top + bed_hull_bottom) / 2.0
    bed_hull = make_box_mesh(
        stage, collision.GetPath().AppendChild("Hull_Bed"),
        (GOAT_BED_HALF_X, bed_hull_half_y, GOAT_BED_HALF_Z),
    )
    UsdGeom.Xformable(bed_hull).AddTranslateOp().Set(
        Gf.Vec3d(0, bed_hull_center_y, GOAT_BED_CENTER_Z)
    )

    # --- Driver seat / exit point hardpoints (§1.6, §2.3) ---------------
    add_hardpoint(hardpoints, "DriverSeat", (-0.35, GOAT_DECK_Y + 0.3, cab_lower_z))
    add_hardpoint(hardpoints, "ExitPoint", (-GOAT_CAB_HALF_WIDTH - 0.5, GOAT_DECK_Y - 0.3, cab_lower_z))

    # --- Reference the wheel corners into the assembly ------------------
    _reference_wheel_corner(stage, rig, "WheelCorner_FL", front_corner_path,
                             (-GOAT_TRACK_X, GOAT_TIRE_RADIUS, GOAT_FRONT_WHEEL_Z))
    _reference_wheel_corner(stage, rig, "WheelCorner_FR", front_corner_path,
                             (GOAT_TRACK_X, GOAT_TIRE_RADIUS, GOAT_FRONT_WHEEL_Z))
    _reference_wheel_corner(stage, rig, "WheelCorner_RL", rear_corner_path,
                             (-GOAT_TRACK_X, GOAT_TIRE_RADIUS, GOAT_REAR_WHEEL_Z))
    _reference_wheel_corner(stage, rig, "WheelCorner_RR", rear_corner_path,
                             (GOAT_TRACK_X, GOAT_TIRE_RADIUS, GOAT_REAR_WHEEL_Z))

    stage.GetRootLayer().Save()

    usdz_path, glb_path = asset_output_paths(MODELS_DIR, "Vehicle", name)
    export_usdz(stage, usdz_path)
    export_gltf(stage, glb_path)
    print(f"Exported {usdz_path.name}, {glb_path.name}")


def build_vehicle_roster():
    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    build_mule()
    build_goat()


if __name__ == "__main__":
    build_vehicle_roster()
