"""Sample OpenUSD asset pipeline entry point.

Demonstrates the pattern every asset script in `pipeline/` should follow:
author with `usd_utils` helpers (so materials/colors survive DCC and web-loader
import, not just usdview), writing intermediate layers under `pipeline/.build/`,
then hand the finished stage to `export_utils` to produce two artifacts in
`public/assets/models/`:

- `model.usdz` -- the authoritative, self-contained OpenUSD interchange file
  (for DCC tools, review, archival).
- `model.glb` -- what the web runtime actually loads. Neither Babylon.js nor
  three.js reliably imports USD/usdz at runtime (see the usd-dcc-export
  skill), so `export_gltf()` converts via headless Blender instead.
"""
from pathlib import Path

from export_utils import export_gltf, export_usdz
from usd_utils import create_stage, make_box_mesh, set_color

ROOT = Path(__file__).resolve().parent.parent
BUILD_DIR = ROOT / "pipeline" / ".build"
MODELS_DIR = ROOT / "public" / "assets" / "models"

STAGE_PATH = BUILD_DIR / "model.usda"
USDZ_PATH = MODELS_DIR / "model.usdz"
GLB_PATH = MODELS_DIR / "model.glb"


def build_sample_scene():
    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    if STAGE_PATH.exists():
        STAGE_PATH.unlink()  # Usd.Stage.CreateNew refuses to overwrite an existing layer

    stage, _ = create_stage(STAGE_PATH, "/World")

    cube = make_box_mesh(stage, "/World/SampleCube", half_extents=(0.5, 0.5, 0.5))
    set_color(cube.GetPrim(), (0.8, 0.2, 0.2))

    stage.GetRootLayer().Save()

    export_usdz(stage, USDZ_PATH)
    print(f"Exported OpenUSD asset to {USDZ_PATH}")

    export_gltf(stage, GLB_PATH)
    print(f"Exported web-runtime asset to {GLB_PATH}")


if __name__ == "__main__":
    build_sample_scene()
