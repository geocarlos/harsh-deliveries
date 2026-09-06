# Module 5 (Addendum): Runner Physical Design

**Status:** Version 0.1 addendum — supplements [Module 2](02-character-and-vehicle-design.md)'s runner roster with the physical/visual design needed for asset production. Per Module 4's own close-out guidance ("a short Version 0.1 addendum noting what changed and why, rather than silently editing history"), this file does **not** modify Modules 1–4 — Module 2 remains the sole source of truth for each runner's personality, motivation, stance, and driving traits. This file adds exactly one new thing per runner: what they look like.

**Why this exists now:** [`docs/architecture/asset-roadmap.md`](../architecture/asset-roadmap.md) scopes runner characters as placeholder-only (a capsule or billboard proxy) through Phase 2, with full rigged humanoid models explicitly deferred to a later, unscheduled phase — Version 0 of the design has no on-foot mission content to build full characters against yet. Physical descriptions are captured here regardless, ahead of when they're needed, because doing it now (while Module 2's characterization is fresh) is cheap, and it lets the Phase 2 placeholders be *informed* placeholders (color-coded per runner, §3) rather than interchangeable gray capsules.

---

## 1. How to Read This File

Each runner entry below assumes Module 2's write-up as read — it is not repeated here. Only new physical fields are added, along the framework in §2. Runner order matches Module 2 §2 (five starting runners, then the wildcard).

---

## 2. Physical Design Framework

Given this pipeline's stylized, hard-surface, low-poly authoring approach (`pipeline/usd_utils.py`'s explicit-Mesh + flat-color-material conventions — no texture painting, no sculpted likeness), physical design here means **silhouette-level, at-a-glance-readable traits**, not a full character-sheet illustration brief:

| Axis | What it governs visually | Why it matters for this pipeline specifically |
|---|---|---|
| **Build** | Height/frame/posture — the silhouette read at capsule-proxy scale and, later, at low-poly humanoid scale | Has to read correctly even as a bare capsule shape (§3) before any detail exists |
| **Signature Prop** | One accessory/gear item reinforcing the character's hook (Module 2) | A single cheap prop reads better at low-poly scale than many small details competing for attention |
| **Palette** | 2–3 dominant colors | The only thing a Phase 2 placeholder can actually show — see §3's placeholder mapping |
| **Wear State** | How "used" their gear/vehicle-adjacent kit reads (pristine vs. field-worn vs. scavenged) | Ties directly to traits Module 2 already established (e.g. high Cargo Care reads as maintained, not necessarily new) — physical design should reinforce mechanical identity, not contradict it |

No new personality content is implied by any of these fields — each is chosen to visually reinforce a trait Module 2 already wrote, not to introduce new characterization.

---

## 3. Runner Physical Profiles

### 3.1 Mara Itoh — "The Ledger"
- **Build:** Slim, upright, economical posture — no wasted movement, nothing to explain away.
- **Signature Prop:** A worn pocket ledger/notebook she still carries physically, even in a world of digital dispatch boards — reads as compulsive tallying made visible.
- **Palette:** Muted neutrals — charcoal, off-white, slate blue. Deliberately unremarkable; nothing that draws a second look, matching her Leverage-over-threats style.
- **Wear State:** Clean and maintained, never scuffed — the one runner whose whole look says "under control," reinforcing her strong Cargo Care.

### 3.2 Diego Salvatierra — "Padre"
- **Build:** Sturdy, weathered, a few years past field-medic fitness but still solid.
- **Signature Prop:** A faded medic's crossbody bag, repurposed for cargo-run tools — old aid-agency patch bleached past legibility.
- **Palette:** Earth tones — olive, sand, rust — with a ghost of aid-agency color (a washed-out blue or red) as the one call-back to his past.
- **Wear State:** Well-worn but cared-for, like tools he trusts — reinforces strong Cargo Care and Terrain Reading without needing new mechanical meaning.

### 3.3 Kass Ferreira — "Kass"
- **Build:** Athletic, coiled, always look like she's already halfway into a decision.
- **Signature Prop:** An empty holster she never draws from — a visual tell for "doesn't ask what's in the crate," not a combat signal.
- **Palette:** Dark utilitarian — black, olive drab, gunmetal — high-contrast against most environments, sharp and fast-reading.
- **Wear State:** Scuffed but squared-away — gear that's been through real use and still gets maintained on schedule, reinforcing strong Nerve/Handling.

### 3.4 Iveta Rusul — "Highland"
- **Build:** Compact, sturdy, built for scrambling over washouts rather than city sidewalks.
- **Signature Prop:** A hand-carved walking stick or a small goat-bone charm tied to her pack — a place-based, personal object, not a corporate/faction one.
- **Palette:** Mountain-corridor tones — moss green, stone gray, weathered brown.
- **Wear State:** Patched, not polished — functional repairs over cosmetic upkeep, matching her impatience with "corporate checkpoint theater" and weak Leverage.

### 3.5 Ren Okafor-Boyle — "Wire"
- **Build:** Youngest and leanest of the roster, restless posture — reads as always about to move.
- **Signature Prop:** A helmet covered in hand-applied stickers/patches marking personal speed records — the character's reputation-chasing motivation made physically visible.
- **Palette:** A worn base (faded denim/canvas) with one or two deliberately bright accent colors (a jacket stripe, the helmet) — the one runner who *wants* to be seen, reinforcing his disregard for Profile concerns.
- **Wear State:** Scuffed and proud of it — dents and patches worn like trophies, not damage to hide, reinforcing the roster's highest cargo-damage-variance runner.

### 3.6 [Wildcard] — "The Warden"
- **Build:** Older, harder, stillness rather than tension — the opposite silhouette read from Kass's coiled energy despite both having strong Nerve.
- **Signature Prop:** A stripped uniform-style jacket with visible ghost-outlines where faction insignia used to be removed — the character's unresolved past made visible without spelling it out, matching Module 2's "stays ambiguous rather than clean redemption."
- **Palette:** Deliberately desaturated and faction-neutral — grays and blacks with none of the regional/personal color cues every other runner gets. This is intentional: the Warden is the one runner with no stance on the region-tension framing (Module 2 §2.6), and the physical design should not accidentally code them into either faction's visual language.
- **Wear State:** Worn but disciplined — "seen worse than this" rather than "roughed up," reinforcing the character's unique Cargo Care + Nerve combination (Module 2's one deliberate exception to the roster balance rule).

---

## 4. Placeholder Mapping (Phase 2 Hand-off)

Direct input for `docs/architecture/asset-roadmap.md`'s Phase 2 "Placeholder Character kit": each runner's **Palette** primary color, applied flat to a capsule or billboard-card proxy (`Character` category, §1.6/§2.1 of the roadmap) so even placeholders are distinguishable at a glance on a dispatch board, with no art dependency yet.

| Runner | Placeholder primary color | Suggested proxy type |
|---|---|---|
| Mara Itoh | Slate blue (`#5A6B7A`) | Billboard card (portrait-style — her whole identity is "read at a glance") |
| Diego Salvatierra | Faded olive (`#7A8450`) | Billboard card |
| Kass Ferreira | Gunmetal (`#3A3F44`) | Capsule (posture/coil reads better as a plain shape than a static portrait) |
| Iveta Rusul | Moss green (`#5C6B4A`) | Capsule |
| Ren Okafor-Boyle "Wire" | Bright accent yellow (`#E0B33C`) over worn base | Billboard card (his motivation is *being seen* — worth showing even as a placeholder) |
| The Warden | Neutral gray (`#4A4A4A`), no accent | Capsule — deliberately the plainest placeholder in the roster, matching §3.6's palette-neutral intent |

This mapping is a Phase 2 authoring input, not a new asset spec — the roadmap's Phase 2 acceptance criteria (one `Anchor` hardpoint per proxy, clean `usdz`/`glb` export) are unchanged by it.

---

## Decisions Log
- **Scope confirmed:** this file adds physical/visual design only; Module 2 remains authoritative for personality, motivation, stance, and driving traits. ✅
- **Full character modeling stays deferred:** captured now for later use, not scheduled into any current phase — see `docs/architecture/asset-roadmap.md`'s "Phase 6 (Deferred)" note. ✅
- **Placeholder proxies get real color-coding, not generic gray:** the §4 mapping is cheap to apply now and removes "which gray blob is which runner" as a Phase 2/3 playtesting confusion. ✅

---

*This addendum does not close or reopen Version 0 — Modules 1–4 remain the approved baseline. Treat this file the same way: diff against it for future changes rather than rewriting in place.*
