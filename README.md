# Harsh Deliveries

*In a world where trust is currency and roads are battlefields, you're the
only thing standing between "the package" and everyone who wants it gone,
exposed, or stolen — deliver it anyway.*

Harsh Deliveries is a **vehicle-based delivery roguelite-lite**: pick a
runner, pick a vehicle, pick a route, and get cargo from Point A to Point B
before terrain, weather, cargo fragility, or armed opposition takes it from
you first. There's no combat-for-its-own-sake and no open-world grinding —
every system exists to put pressure on the drive itself. The full design —
world, roster, systems, and mission structure — lives in
[`docs/game-design/`](docs/game-design/):

1. [Core Mechanics & Narrative Synopsis](docs/game-design/01-core-mechanics-and-narrative-synopsis.md) — pitch, world, design pillars, core loop.
2. [Character & Vehicle Design](docs/game-design/02-character-and-vehicle-design.md) — the runner roster and vehicle roster.
3. [Gameplay & Player Agency](docs/game-design/03-gameplay-and-player-agency.md) — loadout, the Stakes dial, mid-run agency, difficulty scaling.
4. [Mission Design](docs/game-design/04-mission-design.md) — mission template, hazard catalog, sample missions per tier.

These four documents are **Version 0** of the design — approved, but with
numbers (fragility floors, payouts, pursuer counts) deliberately left
untuned pending playtesting. See Module 4's Version 0 Close-Out for the
recommended next step (a vertical slice) before committing to full-scope
asset production.

## How it works

```
pipeline/*.py  →  public/assets/models/<name>.usdz + <name>.glb  →  src/ (Babylon.js)
```

- **`pipeline/`** — Python scripts using the OpenUSD API to author `.usda`
  stages, then export two artifacts per asset: a self-contained `.usdz`
  (the authoritative OpenUSD interchange file, for DCC tools/review) and a
  `.glb` (what the Babylon.js runtime actually loads). Babylon.js has no
  USD/usdz *import* support, so `.glb` — produced by converting the
  flattened stage through headless Blender — is the asset the runtime
  depends on. See `CLAUDE.md` and the `usd-build`/`usd-dcc-export` Claude
  skills for the full rationale and authoring conventions.
- **`src/`** — the TypeScript + Vite + Babylon.js runtime that loads
  `public/assets/models/model.glb`, handles Havok physics, and will grow
  into the game's dispatch board, drive loop, and mission systems as
  described in the design docs above.

## Prerequisites

- **Node.js** (for the web runtime)
- **conda or mamba** ([miniforge](https://github.com/conda-forge/miniforge)),
  for a full OpenUSD build: the PyPI `usd-core` wheel is a stripped build
  with no `usdchecker` CLI and no Hydra/`usdview`, so the pipeline uses
  conda-forge's `openusd` package instead.
- **Blender** (5.x+), used headlessly to convert the pipeline's USD output
  to `.glb`. Make sure `blender` is on `PATH`, or set the
  `BLENDER_EXECUTABLE` env var to its full path.

## Quick start

1. Set up the OpenUSD environment once:

   ```bash
   conda env create -f environment.yml -p ./.conda-env
   ```

   Activate `.conda-env` before running any pipeline command below.

2. Install web runtime dependencies:

   ```bash
   npm install
   ```

3. Generate assets:

   ```bash
   npm run build:assets
   ```

4. Launch the dev server:

   ```bash
   npm run dev
   ```

## Working with Claude Code

This project ships several `.claude/skills/` that load automatically for
the relevant task: `usd-build` and `usd-dcc-export` (OpenUSD authoring and
DCC/web-loader export gotchas) and `babylon-engine` (Babylon.js runtime
conventions — model loading, Havok physics setup). `CLAUDE.md` documents
the project's conventions and known pitfalls in more detail than this
file.

## License

Apache License 2.0 — see [LICENSE](LICENSE).
