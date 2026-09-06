---
name: babylon-engine
description: Use when writing or modifying Babylon.js runtime code (src/) in this template -- loading the OpenUSD pipeline's exported models, Havok physics setup, or anything using @babylonjs/core, @babylonjs/loaders, or @babylonjs/havok.
allowed-tools: Bash, Read, Edit, Write, Grep, Glob
---

# Babylon.js Runtime Notes (this template)

Lessons from getting the initial Babylon.js starter actually working end-to-end
(build + typecheck + real browser render), 2026-09-06. Several of these
contradict a plausible-sounding but nonexistent API — verify against
`node_modules/@babylonjs/*` or current docs before trusting an unfamiliar
Babylon.js API name, the same way this list was built.

## 1. Babylon.js cannot load USD or usdz -- load the pipeline's `.glb` instead

Babylon.js 8.0 added usdz *export* (for iOS AR Quick Look) but there is no
`@babylonjs/loaders/USD` module and no USD/usdz *import* path at all. Never
point `SceneLoader`/`AppendSceneAsync` at the pipeline's `.usdz` output --
it will fail to load. `pipeline/export_utils.py`'s `export_gltf()` converts
the same authored stage to a self-contained `.glb` via headless Blender
specifically because of this gap (see the `usd-dcc-export` skill) -- load
`model.glb` from `public/assets/models/`, not `model.usdz`.

`npm run build:assets` (`python pipeline/build_assets.py`) must succeed and
produce `public/assets/models/model.glb` before the runtime has anything to
load; that step needs Blender installed and either on `PATH` or pointed to
via the `BLENDER_EXECUTABLE` env var.

## 2. Register the glTF loader, and use the current (non-deprecated) load API

```typescript
import { AppendSceneAsync } from '@babylonjs/core';
import '@babylonjs/loaders/glTF';   // registers the glTF/.glb loader plugin

await AppendSceneAsync('/assets/models/model.glb', scene);
```

- `import '@babylonjs/loaders/glTF';` is the registration import (not
  `.../USD`, which doesn't exist).
- Use the **module-level, PascalCase** `AppendSceneAsync` (also
  `LoadSceneAsync`, `ImportMeshAsync`, `LoadAssetContainerAsync`). The
  `SceneLoader` class and its methods (`SceneLoader.AppendAsync`, etc.) are
  deprecated, and so -- confusingly -- is the **lowercase**
  `appendSceneAsync`: check `node_modules/@babylonjs/core/Loading/sceneLoader.d.ts`
  if in doubt about which casing is current for a given version.

## 3. `HemisphericLight`, not `HemisphereLight`

There is no `HemisphereLight` export from `@babylonjs/core` -- it's
`HemisphericLight`. TypeScript will flag this at compile time
(`TS2724: has no exported member named 'HemisphereLight'`), so `npm run
check` catches it, but it's an easy typo to reintroduce from memory.

## 4. Havok + Vite: the WASM needs an explicit `?url` + `locateFile`

A bare `const havokInstance = await HavokPhysics();` fails under Vite (both
`npm run dev` and `vite build`) with:

```
wasm streaming compile failed: TypeError: Failed to execute 'compile' on
'WebAssembly': Incorrect response MIME type. Expected 'application/wasm'.
...
CompileError: WebAssembly.instantiate(): expected magic word 00 61 73 6d,
found 3c 21 44 4f @+0
```

That last hex sequence is literally `<!DO` -- i.e. Vite served back its SPA
fallback `index.html` instead of the wasm binary, because `HavokPhysics()`'s
default internal lookup path for the wasm file doesn't resolve correctly
under Vite's dev server or bundler. Confirmed fix (verified with a real
headless-browser run, not just a typecheck):

```typescript
import HavokPhysics from '@babylonjs/havok';
import havokWasmUrl from '@babylonjs/havok/lib/esm/HavokPhysics.wasm?url';

const havokInstance = await HavokPhysics({ locateFile: () => havokWasmUrl });
```

- The `?url` suffix is a Vite import convention that resolves to the final
  served/bundled URL of that asset, in both `npm run dev` and `vite build`.
- The exact sub-path (`lib/esm/HavokPhysics.wasm`) comes from the installed
  package's actual layout -- check
  `node_modules/@babylonjs/havok/lib/esm/` if a future version moves it.
- This requires `"types": ["vite/client"]` in `tsconfig.json` (already set
  in this template) so the `?url` import typechecks -- without it, `tsc`
  reports `Cannot find module '...?url'`.

## 5. Verifying changes to this runtime code

`npm run check` (`tsc --noEmit && vite build`) only proves the code compiles
and bundles -- it does NOT catch the Havok wasm MIME-type failure above,
which only surfaces at actual runtime in a browser. After any change here
that touches asset loading or physics init, actually run `npm run dev` and
load the page (or drive it headlessly, e.g. with Playwright) and check the
browser console for errors -- don't rely on the build passing alone.
