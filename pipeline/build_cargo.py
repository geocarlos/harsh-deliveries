"""Cargo container kit build script (asset-roadmap.md §1.2, Phase 2 Task 1).

Authors and exports all 5 cargo profiles from the roadmap's table, each its
own asset sharing `cargo_utils.add_pallet_base`'s pallet + `TieDown_01..04`
convention, differentiated by container archetype (crate/drum/case/sealed
box) and material only. Each container's Fragility/Legality (gameplay
metadata that doesn't survive the glTF export -- see the Decisions Log
addendum in asset-roadmap.md) is written to a manifest sidecar keyed by the
container's own default-prim name.
"""
from pathlib import Path

import cargo_utils
from export_utils import export_gltf, export_usdz
from manifest_utils import write_manifest
from usd_utils import asset_output_paths, create_asset_stage

ROOT = Path(__file__).resolve().parent.parent
BUILD_DIR = ROOT / "pipeline" / ".build"
MODELS_DIR = ROOT / "public" / "assets" / "models"

# (asset name, archetype builder, color, material preset, fragility, legality)
CARGO_VARIANTS = [
    ("WoodCrate", cargo_utils.build_crate_shell, (0.55, 0.4, 0.22), None, "Low", "Legal"),
    ("GlassCase", cargo_utils.build_case_shell, (0.75, 0.88, 0.9), "glass-preview", "High", "Legal"),
    ("MetalPartsCrate", cargo_utils.build_crate_shell, (0.5, 0.51, 0.53), "steel", "Medium", "Legal"),
    ("SealedContainer", cargo_utils.build_sealed_box_shell, (0.18, 0.18, 0.2), "unmarked-matte", "Low", "Illegal"),
    ("ChemicalDrum", cargo_utils.build_drum_shell, (0.42, 0.44, 0.46), "steel", "High", "Illegal"),
]


def build_cargo_variant(name, shell_builder, color, preset, fragility, legality):
    build_path = BUILD_DIR / f"cargo_{name}.usda"
    if build_path.exists():
        build_path.unlink()  # Usd.Stage.CreateNew refuses to overwrite an existing layer

    stage, scopes = create_asset_stage(build_path, "Cargo", name)
    cargo_utils.add_pallet_base(stage, scopes)
    shell_builder(stage, scopes, color, preset)
    stage.GetRootLayer().Save()

    usdz_path, glb_path = asset_output_paths(MODELS_DIR, "Cargo", name)
    export_usdz(stage, usdz_path)
    export_gltf(stage, glb_path)

    manifest_path = glb_path.parent / f"{glb_path.stem}.manifest.json"
    write_manifest(manifest_path, {
        f"Cargo_{name}": {"fragility": fragility, "legality": legality},
    })

    print(f"Exported {usdz_path.name}, {glb_path.name}, {manifest_path.name}")


def build_cargo_kit():
    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    for variant in CARGO_VARIANTS:
        build_cargo_variant(*variant)


if __name__ == "__main__":
    build_cargo_kit()
