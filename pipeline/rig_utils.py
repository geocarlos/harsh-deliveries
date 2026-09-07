"""Rig-scope and Hardpoints-scope authoring helpers (asset-roadmap.md §2.2,
§2.3): pivot Xforms for animatable parts and zero-geometry marker Xforms.

Pivot suffixes (`_Steer`/`_Spin`/`_Hinge`/`_Latch`) are load-bearing, not
cosmetic -- the Babylon runtime finds animatable nodes by suffix pattern
rather than a per-asset node list (§2.2), so `add_pivot_xform` validates
against that fixed set instead of accepting anything the caller passes.
"""
from pxr import Gf, UsdGeom

_VALID_PIVOT_SUFFIXES = ("_Steer", "_Spin", "_Hinge", "_Latch")
_VALID_AXES = ("X", "Y", "Z")


def add_pivot_xform(parent, name, suffix, translate=(0, 0, 0)):
    """A child UsdGeom.Xform named f"{name}{suffix}" under `parent` (a
    Usd.Prim), for the Rig scope's pivot convention -- the pivot is always
    the parent of the mesh it moves, never a sibling, so the transform
    inherits correctly once exported to glTF.

    Raises ValueError if `suffix` isn't one of _Steer/_Spin/_Hinge/_Latch.

    `translate` is authored as a translate op only if non-zero. Returns the
    new Xform's Prim so the caller can parent a mesh under it (via
    `prim.GetPath()`) and pose it with `set_pivot_rotation`.
    """
    if suffix not in _VALID_PIVOT_SUFFIXES:
        raise ValueError(
            f"Invalid pivot suffix {suffix!r}; must be one of {_VALID_PIVOT_SUFFIXES}"
        )
    stage = parent.GetStage()
    path = parent.GetPath().AppendChild(f"{name}{suffix}")
    xform = UsdGeom.Xform.Define(stage, path)
    if any(translate):
        xform.AddTranslateOp().Set(Gf.Vec3d(*translate))
    return xform.GetPrim()


def set_pivot_rotation(pivot_prim, axis, degrees=0.0):
    """Author a single rotate op on `pivot_prim` about `axis` ("X"/"Y"/"Z")
    to pose a Rig pivot at author time -- a fixed pose, not runtime
    animation (driving this same op at runtime is the Babylon side's job).

    `axis` is a parameter rather than hardcoded per suffix: the roadmap's
    worked example uses rotateY for steering/hinge and rotateX for
    spin/latch, but a future pivot (e.g. a horizontal gate-arm hinge) may
    need a different axis than today's vertical door hinge.

    Calling this again on the same prim replaces the existing rotate op's
    value rather than stacking a second rotate op, since this pipeline's
    convention is exactly one rotate op per pivot.
    """
    if axis not in _VALID_AXES:
        raise ValueError(f"Invalid axis {axis!r}; must be one of {_VALID_AXES}")
    xformable = UsdGeom.Xformable(pivot_prim)
    op_type = getattr(UsdGeom.XformOp, f"TypeRotate{axis}")
    op = next((o for o in xformable.GetOrderedXformOps() if o.GetOpType() == op_type), None)
    if op is None:
        op = getattr(xformable, f"AddRotate{axis}Op")()
    op.Set(float(degrees))
    return op


def add_hardpoint(parent, name, translate):
    """A zero-geometry marker Xform (translate-only, no mesh, no rotate)
    under `parent` (a Usd.Prim), named exactly `name` (§2.3) -- its world
    position is the payload, not its appearance. The caller supplies the
    full name (e.g. "TieDown_01", "DriverSeat", "ConnectOut"); this helper
    doesn't invent naming conventions of its own.
    """
    stage = parent.GetStage()
    path = parent.GetPath().AppendChild(name)
    xform = UsdGeom.Xform.Define(stage, path)
    xform.AddTranslateOp().Set(Gf.Vec3d(*translate))
    return xform.GetPrim()
