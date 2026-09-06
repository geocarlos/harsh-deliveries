---
name: usd-build
description: Use when creating, modifying, or inspecting 3D assets and scenes using Python and OpenUSD (pxr framework) in this repo's asset pipeline.
allowed-tools: Bash
---

# OpenUSD Scene Generation Workflow (this repo)

When requested to build or modify a 3D asset/scene for `pipeline/`:

1. **Environment**: Activate the project's conda environment before running
   any Python (`conda env create -f environment.yml -p ./.conda-env`, once).
   The PyPI `usd-core` wheel is a stripped "core" build with no `usdchecker`
   CLI and no Hydra/`usdview` — conda-forge's `openusd` package is the full
   build. See `environment.yml` and the repo `CLAUDE.md` for details.
2. **Reuse helpers**: Import from `pipeline/usd_utils.py` (stage setup, mesh
   + material helpers) instead of re-deriving them per script. Prefer
   `make_box_mesh` / `make_cylinder_mesh` over `UsdGeom.Cube` / `Cylinder`
   whenever the part needs a bound material downstream — several consumers
   (e.g. Blender's USD importer) only bind materials to real `Mesh` prims,
   not implicit Gprims.
3. **Define Stage**: Use `usd_utils.create_stage()` so up-axis,
   meters-per-unit, and `SetDefaultPrim()` are set consistently. Write
   intermediate authored layers under `pipeline/.build/` (gitignored) —
   never directly into `public/assets/models/`, which holds only final
   packaged `.usdz` files.
4. **Generate Code**: Implement the requested schemas/hierarchy. Bind color
   with `usd_utils.set_color()` (authors `displayColor` AND binds a real
   `UsdShade.Material`) rather than displayColor alone, which some
   consumers ignore for shading.
5. **Export**: Produce both artifacts in `public/assets/models/`: call
   `export_utils.export_usdz()` for the authoritative `<name>.usdz`, and
   `export_utils.export_gltf()` for the `<name>.glb` the web runtime actually
   loads (neither Babylon.js nor three.js reliably loads USD/usdz at
   runtime — see the `usd-dcc-export` skill). `export_gltf()` drives headless
   Blender, so it requires a Blender install (`BLENDER_EXECUTABLE` env var if
   not on `PATH`). If the stage contains any `UsdGeom.PointInstancer`, call
   `export_utils.bake_all_point_instancers()` first — instancing is not
   reliably supported by every downstream consumer. **Never** call
   `Usd.Stage.CreateNew()` directly on a `.usdz` path: usdz is a read-only
   layer format and this fails at runtime.
6. **Validate**: Run `usdchecker <file>` via Bash. If errors exist, fix the
   script and re-run.
7. **Inspect**: Run `usdtree <file>` to confirm the prim hierarchy matches
   intent (e.g. a `Mesh` with a bound `Material`, not a bare `Cube`).
8. If the asset needs to render correctly outside `usdview` (Blender, glTF
   converters, or a web loader), see the `usd-dcc-export` skill for known
   PointInstancer/material/visibility gaps before considering the export
   final — passing `usdchecker` only proves the file is spec-valid, not
   that every consumer renders every prim.
