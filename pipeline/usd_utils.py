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


def make_mesh(stage, path, points, face_vertex_counts, face_vertex_indices):
    """An explicit UsdGeom.Mesh with flat per-face normals, double-sided (to
    tolerate inconsistent hand-authored winding), and extent authored from
    its own points."""
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
    return mesh


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
    return make_mesh(stage, path, points, face_vertex_counts, face_vertex_indices)


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
    return make_mesh(stage, path, points, face_vertex_counts, face_vertex_indices)


_material_cache = {}


def get_material(stage, color):
    """One UsdPreviewSurface material per unique (stage, color) pair, shared
    across prims, so displayColor also renders in tools (e.g. Blender) that
    only shade from bound materials and ignore the bare displayColor
    primvar."""
    key = (id(stage), color)
    if key not in _material_cache:
        name = "Mat_{:02x}{:02x}{:02x}".format(*(round(c * 255) for c in color))
        mat_path = f"/{stage.GetDefaultPrim().GetName()}/Materials/{name}"
        material = UsdShade.Material.Define(stage, mat_path)
        shader = UsdShade.Shader.Define(stage, f"{mat_path}/PreviewSurface")
        shader.CreateIdAttr("UsdPreviewSurface")
        shader.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).Set(Gf.Vec3f(*color))
        shader.CreateOutput("surface", Sdf.ValueTypeNames.Token)
        material.CreateSurfaceOutput().ConnectToSource(shader.ConnectableAPI(), "surface")
        _material_cache[key] = material
    return _material_cache[key]


def set_color(prim, color):
    """Author displayColor AND bind a real material for it. Note
    `.Apply(prim)`, not just `UsdShade.MaterialBindingAPI(prim)` -- the
    latter authors the binding relationship but not the required
    apiSchemas metadata entry, which usdchecker's
    MaterialBindingAPIAppliedChecker flags."""
    UsdGeom.Gprim(prim).CreateDisplayColorAttr(Vt.Vec3fArray([Gf.Vec3f(*color)]))
    UsdShade.MaterialBindingAPI.Apply(prim).Bind(get_material(prim.GetStage(), color))
