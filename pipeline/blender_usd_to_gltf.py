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
import sys

import bpy

argv = sys.argv[sys.argv.index("--") + 1:]
input_path, output_path = argv[0], argv[1]

# Blender's startup scene ships a default Cube/Camera/Light -- remove them so
# they don't leak into the export.
for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj, do_unlink=True)

bpy.ops.wm.usd_import(filepath=input_path)

bpy.ops.export_scene.gltf(
    filepath=output_path,
    export_format="GLB",
    export_yup=True,  # glTF is Y-up; our stages already author Y-up (see usd_utils.create_stage)
    export_animations=True,
    export_materials="EXPORT",
)

print(f"Converted {input_path} -> {output_path}")
