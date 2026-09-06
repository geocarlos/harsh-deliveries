# OpenUSD Web Engine Template

## Core Architecture
- **Pipeline:** Python scripts (`pipeline/`) use the OpenUSD API to author `.usd`/`.usda` models, then export two artifacts into `public/assets/models/`: a self-contained `.usdz` (authoritative OpenUSD interchange) and a `.glb` (what the web runtime actually loads — see Asset Pipeline below for why both exist).
- **Runtime:** TypeScript + Vite web runtime loading the pipeline's exported `.glb` models.
- **Workflow:** Code-first asset generation and logic. No visual editors.

## Commands
- `python pipeline/build_assets.py` — Run OpenUSD Python asset pipeline.
- `npm run dev` — Launch Vite local development server.
- `npm run check` — Run TypeScript type checking and Vite build verification.

## OpenUSD Environment
- Requires the **conda-forge `openusd` package**, not the PyPI `usd-core` wheel: the PyPI build is a stripped "core" build with no `usdchecker` CLI and no Hydra/`usdview`, while conda-forge's `openusd` is the full build (also gets you `usdview` for free).
- One-time setup: `conda env create -f environment.yml -p ./.conda-env`. Activate that environment before running any pipeline command.
- Also requires a **Blender** install (5.x+) for `export_utils.export_gltf()`'s USD→glTF conversion (see Asset Pipeline below). Set the `BLENDER_EXECUTABLE` env var to its full path if `blender` isn't on `PATH`.

## OpenUSD Python Coding Guidelines
- **Imports:** Standard bindings only — `Usd`, `UsdGeom`, `UsdShade`, `Sdf`, `Gf`, `Vt` from `pxr`.
- **Shared helpers:** Use `pipeline/usd_utils.py` (stage setup, mesh + material helpers) and `pipeline/export_utils.py` (PointInstancer baking + `.usdz`/`.glb` export) rather than re-deriving them per asset script.
- **Stage setup:** Every new stage sets up-axis (`UsdGeom.SetStageUpAxis`), meters-per-unit (`UsdGeom.SetStageMetersPerUnit`), and `SetDefaultPrim()` — `usd_utils.create_stage()` does all three consistently.
- **Geometry:** Prefer explicit `UsdGeom.Mesh` (via `usd_utils.make_box_mesh` / `make_cylinder_mesh`) over implicit Gprims (`Cube`, `Cylinder`, `Sphere`, `Cone`). Several downstream consumers (e.g. Blender's USD importer) only bind materials to real meshes, not implicit primitives.
- **Color/Material:** Never rely on bare `primvars:displayColor` alone — pair it with a real `UsdShade.Material` (`UsdPreviewSurface`) bound via `UsdShade.MaterialBindingAPI.Apply(prim).Bind(...)`. Use `usd_utils.set_color()`, which does both and caches one material per (stage, color).
- **Instancing:** `UsdGeom.PointInstancer` is not reliably supported by every downstream consumer (DCC tools or web loaders). Before exporting, bake any instancers with `export_utils.bake_all_point_instancers()`.

## Asset Pipeline
- Author stages under `pipeline/.build/` (gitignored intermediate `.usda`/`.usdc` files); only the final packaged assets belong in `public/assets/models/`.
- Every asset script should produce **both** artifacts in `public/assets/models/`: `<name>.usdz` (authoritative OpenUSD interchange, via `export_utils.export_usdz()`) and `<name>.glb` (the web-runtime-loadable asset, via `export_utils.export_gltf()`). Neither Babylon.js nor three.js reliably loads USD/usdz at runtime — Babylon.js has no USD/usdz *import* loader at all (only usdz *export*, for iOS AR Quick Look), and three.js's USD/usdz importer is experimental (no proper transform hierarchy in places, no skinning/animation) — so `export_gltf()` converts via headless Blender instead of relying on either engine to load USD directly.
- **Never** write directly to a `.usdz` path with `Usd.Stage.CreateNew()` — USD's usdz file format is read-only as a layer format, and this fails at runtime ("creating package usdz layer is not allowed through this API"). Always flatten the composed stage to a normal layer first, then package it with `UsdUtils.CreateNewUsdzPackage()` — this is exactly what `export_utils.export_usdz()` does.
- **Validation:** Run `usdchecker` on the flattened layer or final `.usdz` before considering a pipeline change complete. Passing `usdchecker` only proves the file is spec-valid — it does not guarantee every downstream consumer renders every prim (see the `usd-dcc-export` skill for known gaps: PointInstancer support, displayColor-only shading, implicit-Gprim material bindings).

## Development Rules
- **Code Style:** Strict TypeScript. Prefer clear type definitions and modular files.
- **Frame Loops:** Never trigger React/DOM re-renders inside 60 FPS animation or physics frame loops. Use mutable refs or direct object updates.
- **Verification:** Always run `npm run check` after modifying runtime code to ensure zero compilation or build errors.


## Babylon.js Engine Rules
- **Loader:** Babylon.js has no USD/usdz *import* support (only usdz *export*, added in 8.0, for iOS AR Quick Look) -- never load the pipeline's `.usdz` output directly. Load the pipeline's `.glb` output (produced by `pipeline/export_utils.py`'s `export_gltf()` via headless Blender) with `import '@babylonjs/loaders/glTF';` + the module-level `AppendSceneAsync(...)` (the `SceneLoader` class and its `.AppendAsync`/`.ImportMeshAsync` methods, and the lowercase `appendSceneAsync`, are all deprecated in favor of this PascalCase module-level function).
- **Physics:** Havok needs its WASM module initialized before use: `const havokInstance = await HavokPhysics()` (from `@babylonjs/havok`), then `scene.enablePhysics(gravity, new HavokPlugin(true, havokInstance))`. Under Vite, a bare `HavokPhysics()` call fails ("Incorrect response MIME type") because the wasm request falls through Vite's SPA fallback -- import the wasm with `?url` (`import havokWasmUrl from '@babylonjs/havok/lib/esm/HavokPhysics.wasm?url'`) and pass `HavokPhysics({ locateFile: () => havokWasmUrl })`. This requires `"types": ["vite/client"]` in `tsconfig.json` (already set) so the `?url` import typechecks.
- **Scene Tree:** Attach interactive logic via scene component classes or custom ActionManagers.
