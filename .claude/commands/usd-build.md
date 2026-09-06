---
description: Build or modify a 3D asset using Python and OpenUSD for this repo's pipeline
allowed-tools: Bash(python:*), Bash(conda:*), Bash(usdchecker:*), Bash(usdtree:*)
argument-hint: [3D asset prompt or specifications]
---

Execute the following steps for the requested asset: "$ARGUMENTS":

1. **Design Stage Hierarchy**: Map out Xforms, meshes, and material bindings,
   reusing `pipeline/usd_utils.py` helpers rather than re-deriving them.
2. **Write Python Script**: Add or modify a script under `pipeline/`,
   authoring into `pipeline/.build/` and exporting the final `.usdz` via
   `pipeline/export_utils.py`.
3. **Execute & Generate**: Run the script with the project's conda
   environment active (`environment.yml` / `.conda-env`).
4. **Validate**: Run `usdchecker` on the flattened layer or final `.usdz`.
   If errors exist, fix the script and re-run.
5. **Inspect**: Run `usdtree` on the output to confirm the prim hierarchy —
   real `Mesh` prims with bound `Material`s, not bare implicit Gprims.
