"""Runs INSIDE Blender's own Python via `blender --background --python`, not
the project's conda environment -- see export_utils.export_gltf().

Converts a flattened USD layer to a single self-contained .glb: Blender's
native USD importer handles UsdPreviewSurface materials and real UsdGeom.Mesh
geometry (the conventions pipeline/usd_utils.py already enforces) far more
reliably than any pure-Python USD->glTF converter, and glTF/.glb is the
best-supported native import format for both Babylon.js and three.js -- see
the usd-dcc-export skill for why USD/usdz import support in web loaders is
inconsistent or missing outright.

Usage: blender --background --python blender_usd_to_gltf.py -- <in.usdc> <out.glb>
"""
import re
import sys

import bpy

argv = sys.argv[sys.argv.index("--") + 1:]
input_path, output_path = argv[0], argv[1]

# Blender's startup scene ships a default Cube/Camera/Light -- remove them so
# they don't leak into the export.
for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj, do_unlink=True)

# merge_parent_xform=False: Blender's default (True) elides any Xform prim
# with no authored xformOps and exactly one child, reparenting that child up
# a level. A Rig pivot authored at zero relative offset (e.g. a _Spin pivot
# nested directly under _Steer at the same point -- the common, roadmap-
# specified case) has no authored ops and exactly one child (its mesh), so
# the default setting silently drops it from the imported scene -- breaking
# the pivot-is-parent convention the Babylon runtime's suffix lookup depends
# on. Confirmed via a headless-Blender diagnostic (Phase 1 validation).
bpy.ops.wm.usd_import(filepath=input_path, merge_parent_xform=False)

# A vehicle that references the SAME wheel-corner sub-asset at more than one
# position (e.g. one front-corner asset referenced at both FL and FR --
# phase3b-mule prompt, Task 4) authors the exact same pivot leaf names
# ("Wheel_Steer", "Wheel_Spin", ...) at more than one USD prim path. USD has
# no problem with this (the ABSOLUTE paths are still unique), but Blender's
# object namespace is flat, so its USD importer auto-deduplicates every
# repeat by appending ".001", ".002", ... AFTER our own suffix -- e.g.
# "Wheel_Spin" -> "Wheel_Spin.001" -- which silently breaks the roadmap's
# §2.2 suffix-lookup convention (`name.endsWith("_Spin")`) for every
# occurrence but the first. Confirmed via an actual Babylon-side load: only
# 1 of 4 `_Spin` nodes and 1 of 2 `_Steer` nodes survived the round trip
# with a usable name. Move Blender's dedup tag to BEFORE our suffix instead
# of after it, so every renamed object still ends with the exact suffix the
# runtime looks up.
_PIVOT_SUFFIXES = ("_Steer", "_Spin", "_Hinge", "_Latch")
_DEDUP_RE = re.compile(r"^(.*)(" + "|".join(_PIVOT_SUFFIXES) + r")\.(\d+)$")
for obj in bpy.data.objects:
    match = _DEDUP_RE.match(obj.name)
    if match:
        prefix, suffix, dedup_num = match.groups()
        obj.name = f"{prefix}_{dedup_num}{suffix}"

bpy.ops.export_scene.gltf(
    filepath=output_path,
    export_format="GLB",
    export_yup=True,  # glTF is Y-up; our stages already author Y-up (see usd_utils.create_stage)
    export_animations=True,
    export_materials="EXPORT",
)

print(f"Converted {input_path} -> {output_path}")
