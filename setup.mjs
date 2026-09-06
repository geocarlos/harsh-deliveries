import fs from 'node:fs';
import path from 'node:path';
import readline from 'node:readline';
import { execSync } from 'node:child_process';

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
});

const question = (query) => new Promise((resolve) => rl.question(query, resolve));

async function main() {
  console.log('\n=============================================');
  console.log(' OpenUSD Engine Template Initialization');
  console.log('=============================================\n');

  console.log('Select target framework:');
  console.log('  [1] Babylon.js  (Games, Interactive Simulations, Havok Physics)');
  console.log('  [2] Three.js    (Cinematic Video, Frame-Accurate Captures)\n');

  const choice = await question('Enter choice (1 or 2): ');
  rl.close();

  const isBabylon = choice.trim() === '1';
  const targetEngine = isBabylon ? 'babylon' : 'three';

  console.log(`\nInitializing project for: ${isBabylon ? 'Babylon.js' : 'Three.js'}...\n`);

  // 1. Setup Directories
  const dirs = [
    'pipeline',
    'src',
    'public/assets/models',
    `.claude/skills/${targetEngine}-engine`
  ];
  dirs.forEach(d => fs.mkdirSync(d, { recursive: true }));

  // 2. Prune unused skill context
  const unusedEngine = isBabylon ? 'three' : 'babylon';
  const unusedSkillPath = path.join('.claude', 'skills', `${unusedEngine}-engine`);
  if (fs.existsSync(unusedSkillPath)) {
    fs.rmSync(unusedSkillPath, { recursive: true, force: true });
  }

  // 3. Write package.json
  const dependencies = isBabylon
    ? { '@babylonjs/core': '^7.0.0', '@babylonjs/loaders': '^7.0.0', '@babylonjs/havok': '^1.3.0' }
    : { 'three': '^0.160.0' };

  const devDependencies = isBabylon
    ? { 'typescript': '^5.3.0', 'vite': '^5.0.0' }
    : { 'typescript': '^5.3.0', 'vite': '^5.0.0', '@types/three': '^0.160.0' };

  const pkgJson = {
    name: `openusd-${targetEngine}-project`,
    private: true,
    version: '0.1.0',
    type: 'module',
    scripts: {
      dev: 'vite',
      build: 'tsc && vite build',
      check: 'tsc --noEmit && vite build',
      preview: 'vite preview',
      'build:assets': 'python pipeline/build_assets.py'
    },
    dependencies,
    devDependencies
  };

  fs.writeFileSync('package.json', JSON.stringify(pkgJson, null, 2));

  // 4. Write Vite & TS Configurations
  fs.writeFileSync('vite.config.ts', `import { defineConfig } from 'vite';\n\nexport default defineConfig({\n  publicDir: 'public',\n  server: { open: true }\n});\n`);

  fs.writeFileSync('tsconfig.json', JSON.stringify({
    compilerOptions: {
      target: 'ES2022',
      module: 'ESNext',
      moduleResolution: 'bundler',
      strict: true,
      skipLibCheck: true,
      isolatedModules: true,
      types: ['vite/client']
    },
    include: ['src']
  }, null, 2));

  // 5. Append Engine Rules to CLAUDE.md
  const engineRules = isBabylon
    ? `\n\n## Babylon.js Engine Rules
- **Loader:** Babylon.js has no USD/usdz *import* support (only usdz *export*, added in 8.0, for iOS AR Quick Look) -- never load the pipeline's \`.usdz\` output directly. Load the pipeline's \`.glb\` output (produced by \`pipeline/export_utils.py\`'s \`export_gltf()\` via headless Blender) with \`import '@babylonjs/loaders/glTF';\` + the module-level \`AppendSceneAsync(...)\` (the \`SceneLoader\` class and its \`.AppendAsync\`/\`.ImportMeshAsync\` methods, and the lowercase \`appendSceneAsync\`, are all deprecated in favor of this PascalCase module-level function).
- **Physics:** Havok needs its WASM module initialized before use: \`const havokInstance = await HavokPhysics()\` (from \`@babylonjs/havok\`), then \`scene.enablePhysics(gravity, new HavokPlugin(true, havokInstance))\`. Under Vite, a bare \`HavokPhysics()\` call fails ("Incorrect response MIME type") because the wasm request falls through Vite's SPA fallback -- import the wasm with \`?url\` (\`import havokWasmUrl from '@babylonjs/havok/lib/esm/HavokPhysics.wasm?url'\`) and pass \`HavokPhysics({ locateFile: () => havokWasmUrl })\`. This requires \`"types": ["vite/client"]\` in \`tsconfig.json\` (already set) so the \`?url\` import typechecks.
- **Scene Tree:** Attach interactive logic via scene component classes or custom ActionManagers.
`
    : `\n\n## Three.js Engine Rules
- **Loader:** three.js does have a \`USDZLoader\` (\`three/addons/loaders/USDZLoader.js\`), but it's experimental (no proper transform hierarchy in places, no skinning/animation) -- never load the pipeline's \`.usdz\` output directly. Load the pipeline's \`.glb\` output (produced by \`pipeline/export_utils.py\`'s \`export_gltf()\` via headless Blender) with \`GLTFLoader\` from \`three/addons/loaders/GLTFLoader.js\` instead. Import addons from \`three/addons/...\`, not the older \`three/examples/jsm/...\` path.
- **Cinematics:** Use deterministic \`step(deltaTime)\` updates (via \`THREE.Clock\`, driven from \`renderer.setAnimationLoop\`) for video export capabilities -- keep scene-state changes inside \`step()\`, not scattered across event handlers, so a frame-accurate capture loop can later drive it with a fixed \`deltaTime\` instead of real elapsed time.
- **Post-Processing:** Manage pass pipelines explicitly with \`EffectComposer\` (\`three/addons/postprocessing/EffectComposer.js\`).
`;

  fs.appendFileSync('CLAUDE.md', engineRules);

  // 6. Write Starter App Code
  const starterApp = isBabylon
    ? `import { Engine, Scene, ArcRotateCamera, Vector3, HemisphericLight, AppendSceneAsync, HavokPlugin } from '@babylonjs/core';
import '@babylonjs/loaders/glTF';
import HavokPhysics from '@babylonjs/havok';
// Vite's dev server serves a raw \`HavokPhysics()\` fetch with the wrong MIME
// type (falls through to the SPA HTML fallback instead of the wasm binary).
// The \`?url\` import resolves to the correct built/served asset URL in both
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
`
    : `import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
camera.position.set(0, 1, 5);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;

const light = new THREE.DirectionalLight(0xffffff, 1);
light.position.set(1, 1, 1).normalize();
scene.add(light);
scene.add(new THREE.AmbientLight(0xffffff, 0.3));

// Load the web-runtime asset the OpenUSD pipeline produces. three.js does
// have a USDZLoader (three/addons/loaders/USDZLoader.js), but it's
// experimental (no proper transform hierarchy in places, no
// skinning/animation) -- see pipeline/export_utils.py's export_gltf() for
// how model.glb gets generated from the pipeline's USD source, and the
// usd-dcc-export skill for the full write-up.
const loader = new GLTFLoader();
loader.load(
  '/assets/models/model.glb',
  (gltf) => scene.add(gltf.scene),
  undefined,
  () => console.log('No default model.glb found in public/assets/models/. Run the OpenUSD pipeline first (npm run build:assets).')
);

const clock = new THREE.Clock();

// A deterministic per-frame update decoupled from wall-clock time, so a
// frame-accurate capture loop can later drive this with a fixed deltaTime
// instead of requestAnimationFrame's/setAnimationLoop's real elapsed time.
function step(deltaTime: number) {
  controls.update();
}

renderer.setAnimationLoop(() => {
  step(clock.getDelta());
  renderer.render(scene, camera);
});

window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});
`;

  fs.writeFileSync('src/main.ts', starterApp);

  // 7. Write index.html
  const htmlContent = `<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>OpenUSD ${isBabylon ? 'Babylon.js' : 'Three.js'} App</title>
    <style>
      body { margin: 0; overflow: hidden; background: #111; }
      #renderCanvas, canvas { width: 100vw; height: 100vh; display: block; }
    </style>
  </head>
  <body>
    ${isBabylon ? '<canvas id="renderCanvas"></canvas>' : ''}
    <script type="module" src="/src/main.ts"></script>
  </body>
</html>`;

  fs.writeFileSync('index.html', htmlContent);

  // 8. pipeline/build_assets.py, usd_utils.py, and export_utils.py already
  // ship committed in this template (framework-agnostic OpenUSD pipeline) --
  // nothing to scaffold here.

  console.log('Installing npm dependencies...');
  execSync('npm install', { stdio: 'inherit' });

  console.log('\nInitialization complete!');
  console.log('Run "npm run dev" to launch your web application.\n');
}

main().catch(console.error);