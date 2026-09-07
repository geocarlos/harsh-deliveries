"""Sidecar-manifest fallback for the metadata-strategy risk flagged in
asset-roadmap.md §2.4: whether USD `customData` survives Blender's glTF
export as node `extras` is not yet verified in this codebase (that's Phase
1's job). This helper is built now so it's ready regardless of which way
that test resolves -- it is not wired into any asset script yet.
"""
import json
from pathlib import Path


def write_manifest(path, data):
    """Writes `data` (a plain dict) as pretty JSON to `path`, creating any
    missing parent directories. Returns `path` as a Path."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        f.write("\n")
    return path
