import { Engine, Scene, ArcRotateCamera, Vector3, HemisphericLight, AppendSceneAsync, HavokPlugin } from '@babylonjs/core';
import '@babylonjs/loaders/glTF';
import HavokPhysics from '@babylonjs/havok';
// Vite's dev server serves a raw `HavokPhysics()` fetch with the wrong MIME
// type (falls through to the SPA HTML fallback instead of the wasm binary).
// The `?url` import resolves to the correct built/served asset URL in both
// dev and prod, which locateFile then points the wasm fetch at.
import havokWasmUrl from '@babylonjs/havok/lib/esm/HavokPhysics.wasm?url';

const canvas = document.getElementById('renderCanvas') as HTMLCanvasElement;
const engine = new Engine(canvas, true);

const createScene = async () => {
  const scene = new Scene(engine);
  const camera = new ArcRotateCamera('camera', Math.PI / 2, Math.PI / 4, 10, Vector3.Zero(), scene);
  camera.attachControl(canvas, true);

  new HemisphericLight('light', new Vector3(1, 1, 0), scene);

  const havokInstance = await HavokPhysics({ locateFile: () => havokWasmUrl });
  scene.enablePhysics(new Vector3(0, -9.8, 0), new HavokPlugin(true, havokInstance));

  // Load the web-runtime asset the OpenUSD pipeline produces. Babylon.js has
  // no USD/usdz import loader, only glTF -- see pipeline/export_utils.py's
  // export_gltf() for how model.glb gets generated from the pipeline's USD source.
  try {
    await AppendSceneAsync('/assets/models/model.glb', scene);
  } catch (e) {
    console.log('No default model.glb found in public/assets/models/. Run the OpenUSD pipeline first (npm run build:assets).');
  }

  return scene;
};

createScene().then((scene) => {
  engine.runRenderLoop(() => scene.render());
  window.addEventListener('resize', () => engine.resize());
});
