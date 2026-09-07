"""Shared OpenUSD authoring helpers for the asset pipeline.

Centralizes patterns that keep exported assets renderable across every
downstream consumer (Blender, glTF converters, and web loaders), not just
usdview/Hydra:
- explicit UsdGeom.Mesh instead of implicit Gprims (Cube/Cylinder/...), since
  some importers only bind materials to real meshes, not implicit primitives.
- one cached UsdShade.Material (UsdPreviewSurface) per (stage, color), bound
  via MaterialBindingAPI, since bare `displayColor` alone doesn't render in
  every consumer.
"""
import math

from pxr import Gf, Sdf, Usd, UsdGeom, UsdShade, Vt


def create_stage(file_path, default_prim_path, up_axis=UsdGeom.Tokens.y, meters_per_unit=1.0):
    """A new stage with up-axis, meters-per-unit, and SetDefaultPrim() all
    set consistently. Returns (stage, default_prim_xform)."""
    stage = Usd.Stage.CreateNew(str(file_path))
    UsdGeom.SetStageUpAxis(stage, up_axis)
    UsdGeom.SetStageMetersPerUnit(stage, meters_per_unit)
    default_prim = UsdGeom.Xform.Define(stage, default_prim_path)
    stage.SetDefaultPrim(default_prim.GetPrim())
    return stage, default_prim


_VALID_ASSET_CATEGORIES = ("Vehicle", "Cargo", "Terrain", "Hazard", "Prop", "Character")
_ASSET_SCOPE_NAMES = ("Geometry", "Rig", "Hardpoints", "Collision", "Materials")


def create_asset_stage(file_path, category, name):
    """Wraps create_stage() to author the roadmap §2.1 standardized scope
    skeleton consistently:

        /<Category>_<AssetName>          Xform, default prim
          /Geometry                      Scope
          /Rig                           Scope
          /Hardpoints                    Scope
          /Collision                     Scope
          /Materials                     Scope

    `category` is validated against the fixed §2.1 set (Vehicle, Cargo,
    Terrain, Hazard, Prop, Character) -- this naming contract is relied on by
    later tooling (e.g. the glTF exporter's single-root-node-per-asset
    assumption), so a typo (e.g. "Vehcile") raises here rather than silently
    authoring a misnamed default prim.

    Returns (stage, scopes), where `scopes` is a dict keyed by scope name
    ("Geometry"/"Rig"/"Hardpoints"/"Collision"/"Materials") mapping to that
    Scope's Usd.Prim -- pass `scopes["Rig"]`, etc. as the `parent` argument
    to rig_utils helpers, or `scopes["Geometry"].GetPath().AppendChild(...)`
    as a mesh path.
    """
    if category not in _VALID_ASSET_CATEGORIES:
        raise ValueError(
            f"Invalid asset category {category!r}; must be one of {_VALID_ASSET_CATEGORIES}"
        )
    default_prim_path = f"/{category}_{name}"
    stage, _ = create_stage(file_path, default_prim_path)
    scopes = {
        scope_name: UsdGeom.Scope.Define(stage, f"{default_prim_path}/{scope_name}").GetPrim()
        for scope_name in _ASSET_SCOPE_NAMES
    }
    return stage, scopes


def compute_flat_face_normals(points, face_vertex_counts, face_vertex_indices):
    """One normal per face, so hard-surface parts shade as flat facets
    instead of Hydra's default smooth per-vertex normals blending them into
    a rounded, softened look."""
    normals = []
    idx = 0
    for count in face_vertex_counts:
        i0, i1, i2 = face_vertex_indices[idx], face_vertex_indices[idx + 1], face_vertex_indices[idx + 2]
        edge1 = points[i1] - points[i0]
        edge2 = points[i2] - points[i0]
        normal = Gf.Cross(edge1, edge2)
        length = normal.GetLength()
        normals.append(normal / length if length > 1e-8 else normal)
        idx += count
    return normals


def make_mesh(stage, path, points, face_vertex_counts, face_vertex_indices, uvs=None, uv_indices=None):
    """An explicit UsdGeom.Mesh with flat per-face normals, double-sided (to
    tolerate inconsistent hand-authored winding), and extent authored from
    its own points.

    `uvs`, if given, is authored as a face-varying `primvars:st` -- one UV
    per entry in `face_vertex_indices` (matching the per-face-varying
    convention `compute_flat_face_normals` already uses for normals, since a
    hard-surface part needs seams at face boundaries rather than smoothly
    shared corner UVs). Pass `uv_indices` alongside `uvs` to index into a
    smaller deduplicated UV array instead of one entry per face-vertex."""
    points_array = Vt.Vec3fArray(points)
    mesh = UsdGeom.Mesh.Define(stage, path)
    mesh.CreatePointsAttr(points_array)
    mesh.CreateFaceVertexCountsAttr(Vt.IntArray(face_vertex_counts))
    mesh.CreateFaceVertexIndicesAttr(Vt.IntArray(face_vertex_indices))
    mesh.CreateSubdivisionSchemeAttr(UsdGeom.Tokens.none)  # keep flat facets
    mesh.CreateDoubleSidedAttr(True)
    mesh.CreateExtentAttr(UsdGeom.PointBased.ComputeExtent(points_array))
    mesh.CreateNormalsAttr(
        Vt.Vec3fArray(compute_flat_face_normals(points, face_vertex_counts, face_vertex_indices))
    )
    mesh.SetNormalsInterpolation(UsdGeom.Tokens.uniform)
    if uvs is not None:
        st = UsdGeom.PrimvarsAPI(mesh).CreatePrimvar(
            "st", Sdf.ValueTypeNames.TexCoord2fArray, UsdGeom.Tokens.faceVarying
        )
        st.Set(Vt.Vec2fArray(uvs))
        if uv_indices is not None:
            st.SetIndices(Vt.IntArray(uv_indices))
    return mesh


_BOX_FACE_UVS = [Gf.Vec2f(0, 0), Gf.Vec2f(1, 0), Gf.Vec2f(1, 1), Gf.Vec2f(0, 1)]


def make_box_mesh(stage, path, half_extents):
    """An explicit box Mesh, in place of UsdGeom.Cube -- some consumers (e.g.
    Blender's USD importer) don't apply bound materials to implicit Gprim
    shapes like Cube/Cylinder, only to real Mesh prims."""
    hx, hy, hz = half_extents
    points = [
        Gf.Vec3f(-hx, -hy, -hz), Gf.Vec3f(hx, -hy, -hz),
        Gf.Vec3f(hx, hy, -hz), Gf.Vec3f(-hx, hy, -hz),
        Gf.Vec3f(-hx, -hy, hz), Gf.Vec3f(hx, -hy, hz),
        Gf.Vec3f(hx, hy, hz), Gf.Vec3f(-hx, hy, hz),
    ]
    face_vertex_counts = [4, 4, 4, 4, 4, 4]
    face_vertex_indices = [
        0, 1, 2, 3,  # -Z
        5, 4, 7, 6,  # +Z
        4, 0, 3, 7,  # -X
        1, 5, 6, 2,  # +X
        4, 5, 1, 0,  # -Y
        3, 2, 6, 7,  # +Y
    ]
    uvs = _BOX_FACE_UVS * 6  # same 0-1 quad mapping repeated per face
    return make_mesh(stage, path, points, face_vertex_counts, face_vertex_indices, uvs=uvs)


def make_cylinder_mesh(stage, path, radius, height, axis="Y", sides=16):
    """An explicit tessellated cylinder Mesh, in place of UsdGeom.Cylinder --
    see make_box_mesh for why. `sides` trades roundness for vertex count; 16
    reads as reasonably round at small-prop scale while staying flat-shaded/
    low-poly -- raise it for parts large enough in frame for facets to read
    as angular rather than round."""
    half_h = height / 2.0
    points = []
    for ring_y in (-half_h, half_h):
        for i in range(sides):
            angle = 2.0 * math.pi * i / sides
            cx = radius * math.cos(angle)
            cz = radius * math.sin(angle)
            if axis == "X":
                points.append(Gf.Vec3f(ring_y, cx, cz))
            elif axis == "Z":
                points.append(Gf.Vec3f(cx, cz, ring_y))
            else:  # "Y"
                points.append(Gf.Vec3f(cx, ring_y, cz))
    # points[0:sides] = bottom ring, points[sides:2*sides] = top ring
    face_vertex_counts = [sides, sides] + [4] * sides
    face_vertex_indices = list(reversed(range(sides))) + list(range(sides, 2 * sides))
    for i in range(sides):
        j = (i + 1) % sides
        face_vertex_indices.extend([i, j, sides + j, sides + i])

    # Caps: simple polar projection onto the unit disk (valid, not
    # art-directed -- texel density doesn't matter for Phase 0). Side quads:
    # unwrap around circumference (u) x height (v), one quad per face so
    # seams don't need shared UVs across faces.
    def polar_uv(i):
        angle = 2.0 * math.pi * i / sides
        return Gf.Vec2f(0.5 + 0.5 * math.cos(angle), 0.5 + 0.5 * math.sin(angle))

    uvs = [polar_uv(i) for i in reversed(range(sides))]  # bottom cap
    uvs += [polar_uv(i) for i in range(sides)]  # top cap
    for i in range(sides):
        u0, u1 = i / sides, (i + 1) / sides
        uvs += [Gf.Vec2f(u0, 0), Gf.Vec2f(u1, 0), Gf.Vec2f(u1, 1), Gf.Vec2f(u0, 1)]

    return make_mesh(stage, path, points, face_vertex_counts, face_vertex_indices, uvs=uvs)


_material_cache = {}

# Roughness/metallic (and, for glass-preview, opacity) presets layered onto
# the same UsdPreviewSurface shader `get_material` already authors. This is
# a placeholder-preview material, not physically-correct transmission --
# UsdPreviewSurface doesn't need to nail real glass here (roadmap §Phase 0).
_MATERIAL_PRESETS = {
    "paint": {"roughness": 0.35, "metallic": 0.0},
    "rubber": {"roughness": 0.9, "metallic": 0.0},
    "glass-preview": {"roughness": 0.05, "metallic": 0.0, "opacity": 0.35},
    "unmarked-matte": {"roughness": 0.85, "metallic": 0.0},
    "steel": {"roughness": 0.3, "metallic": 1.0},
}


def get_material(stage, color, preset=None):
    """One UsdPreviewSurface material per unique (stage, color, preset)
    triple, shared across prims, so displayColor also renders in tools (e.g.
    Blender) that only shade from bound materials and ignore the bare
    displayColor primvar.

    `preset` optionally selects a roughness/metallic (and, for
    "glass-preview", opacity) combination from _MATERIAL_PRESETS, layered on
    top of the same diffuseColor. Leaving it as the default `None` authors
    no roughness/metallic/opacity inputs at all, reproducing this function's
    original flat-color-only behavior exactly -- existing 2-arg call sites
    are unaffected."""
    if preset is not None and preset not in _MATERIAL_PRESETS:
        raise ValueError(f"Invalid material preset {preset!r}; must be one of {tuple(_MATERIAL_PRESETS)}")
    key = (id(stage), color, preset)
    if key not in _material_cache:
        suffix = f"_{preset.replace('-', '_')}" if preset else ""
        name = "Mat_{:02x}{:02x}{:02x}{}".format(*(round(c * 255) for c in color), suffix)
        mat_path = f"/{stage.GetDefaultPrim().GetName()}/Materials/{name}"
        material = UsdShade.Material.Define(stage, mat_path)
        shader = UsdShade.Shader.Define(stage, f"{mat_path}/PreviewSurface")
        shader.CreateIdAttr("UsdPreviewSurface")
        shader.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).Set(Gf.Vec3f(*color))
        if preset is not None:
            values = _MATERIAL_PRESETS[preset]
            shader.CreateInput("roughness", Sdf.ValueTypeNames.Float).Set(values["roughness"])
            shader.CreateInput("metallic", Sdf.ValueTypeNames.Float).Set(values["metallic"])
            if "opacity" in values:
                shader.CreateInput("opacity", Sdf.ValueTypeNames.Float).Set(values["opacity"])
        shader.CreateOutput("surface", Sdf.ValueTypeNames.Token)
        material.CreateSurfaceOutput().ConnectToSource(shader.ConnectableAPI(), "surface")
        _material_cache[key] = material
    return _material_cache[key]


def set_color(prim, color, preset=None):
    """Author displayColor AND bind a real material for it. Note
    `.Apply(prim)`, not just `UsdShade.MaterialBindingAPI(prim)` -- the
    latter authors the binding relationship but not the required
    apiSchemas metadata entry, which usdchecker's
    MaterialBindingAPIAppliedChecker flags.

    `preset` is forwarded to `get_material` (see there for the available
    presets); the default `None` keeps existing 2-arg call sites' behavior
    unchanged."""
    UsdGeom.Gprim(prim).CreateDisplayColorAttr(Vt.Vec3fArray([Gf.Vec3f(*color)]))
    UsdShade.MaterialBindingAPI.Apply(prim).Bind(get_material(prim.GetStage(), color, preset))
