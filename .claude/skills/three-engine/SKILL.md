---
name: three-engine
description: Use when writing or modifying three.js runtime code (src/) in this template -- loading the OpenUSD pipeline's exported models, camera/controls setup, or anything using the `three` package or its addons.
allowed-tools: Bash, Read, Edit, Write, Grep, Glob
---

# three.js Runtime Notes (this template)

Lessons from getting the initial three.js starter actually working end-to-end
(build + typecheck + real browser render), 2026-09-06. Verify an unfamiliar
`three` addon's export name and import path against the installed package
before trusting it from memory or an older tutorial — three.js has moved
addon import conventions before (see below) and file/export names don't
always match what a plausible-sounding guess would produce.

## 1. three.js *does* have a USD/usdz loader, but don't use it for the pipeline's output

Unlike Babylon.js (no USD/usdz import support at all), three.js ships a real
`USDZLoader` at `three/addons/loaders/USDZLoader.js` (note: `USDZLoader`, not
`USDLoader` — no such export or file exists). But it's experimental: no
proper transform hierarchy in places, no skinning/animation, limited
material/texture reconstruction. `pipeline/export_utils.py`'s
`export_gltf()` converts the same authored stage to a self-contained `.glb`
via headless Blender specifically to sidestep this (see the
`usd-dcc-export` skill) — load `model.glb` from `public/assets/models/`
with `GLTFLoader`, not `model.usdz` with `USDZLoader`.

`npm run build:assets` (`python pipeline/build_assets.py`) must succeed and
produce `public/assets/models/model.glb` before the runtime has anything to
load; that step needs Blender installed and either on `PATH` or pointed to
via the `BLENDER_EXECUTABLE` env var.

## 2. Import addons from `three/addons/...`, not `three/examples/jsm/...`

```typescript
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
```

`three/examples/jsm/...` is the older convention and can trigger Vite
warnings about dynamic imports it can't analyze. `three/addons/...` is an
export-map alias to the same files (confirmed present as far back as
`three@0.160.0`, this template's pinned version) and is what current
three.js docs and Vite guides recommend. Both paths currently resolve to
real files, but prefer `addons`.

## 3. Loading the model

```typescript
const loader = new GLTFLoader();
loader.load(
  '/assets/models/model.glb',
  (gltf) => scene.add(gltf.scene),   // gltf.scene is a THREE.Group
  undefined,
  (err) => console.log('load failed', err),
);
```

## 4. The "Cinematics: deterministic step(deltaTime)" rule, concretely

The framework-choice menu frames three.js around cinematic/frame-accurate
capture, so the starter's render loop is built around a `step(deltaTime)`
function fed by `THREE.Clock`, driven through `renderer.setAnimationLoop`
(the modern replacement for a raw `requestAnimationFrame` loop):

```typescript
const clock = new THREE.Clock();

function step(deltaTime: number) {
  controls.update();   // put per-frame scene-state changes here, not in event handlers
}

renderer.setAnimationLoop(() => {
  step(clock.getDelta());
  renderer.render(scene, camera);
});
```

Keeping all per-frame mutation inside `step()` is what makes it possible to
later swap `clock.getDelta()` for a fixed timestep (e.g. `1/24`) when doing
a frame-accurate video capture, without touching the rest of the render
loop.

## 5. Verifying changes to this runtime code

`npm run check` (`tsc --noEmit && vite build`) proves the code compiles and
bundles, but not that the model actually loads and renders — a wrong asset
path or a loader mismatch (e.g. `USDZLoader` pointed at `model.glb`) fails
silently into the `onError` callback, which is easy to miss if you don't
actually run the app. After any change here that touches asset loading,
actually run `npm run dev` and load the page (or drive it headlessly, e.g.
with Playwright) and check the browser console for errors.
