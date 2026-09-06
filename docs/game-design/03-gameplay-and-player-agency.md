# Module 3: Gameplay & Player Agency

**Status:** Approved — Stakes framing, the Bail's cost, and Convoy Backup all confirmed by producer. Proceeding to Module 4 (Mission Design).

This module covers the systems through which the player actually expresses intent run-to-run: loadout choice, opt-in risk-taking, mid-drive decisions, difficulty scaling, and what carries over between contracts. It sits between Module 2 (who/what you can choose) and Module 4 (the missions those choices get applied to) — this is the *shape* of the choices, not yet the specific levels built around them.

---

## 1. The Four Levers

Every contract is ultimately shaped by four player decisions, made in a fixed order:

1. **Runner** (Module 2 §2) — who's driving.
2. **Vehicle** (Module 2 §4) — what they're driving.
3. **Route** — which path through the contract's terrain/threat layout.
4. **Stakes** — how much extra risk the player opts into for extra payout (new this module, §3).

The first three were established in Modules 1–2. Stakes is the missing piece that turns "risk/reward per mission" from something that just happens *to* the player into something the player actively dials up or down — Pillar 3 ("Every Route Is a Negotiation") extended one level further: the player negotiates with the *contract itself*, not just the map.

---

## 2. Pre-Run Loadout Flow

The loadout screen for a given contract should surface, in order: cargo profile (fragility/legality — sets constraints), eligible vehicles (Capacity/legality gates some out entirely, per Module 2 §3), eligible runners (none are hard-gated by contract, but the dispatcher board should visually flag a poor Runner+Vehicle+Cargo match before commit, not hide it as a surprise). This matches Pillar 4 — the game should never let a bad matchup happen resembling a UI trap; the cost of a mismatch is a play decision, not a reading-comprehension test.

Route selection happens either at loadout (for contracts with a small number of discrete route options, e.g. tier 1–3) or as an in-drive fork (§4) for contracts designed around a commit-under-pressure moment — which style a given contract uses is a Module 4 mission-design decision, not fixed here.

---

## 3. The Stakes Dial — Opt-In Risk for Opt-In Reward

**Concept:** Before committing to a run, the player can accept one or more **Special Conditions** the client offers for a payout bonus — framed diegetically as the client asking for something extra, not as an abstract difficulty slider. Examples:

- **"No Escort Frequency"** — disables the optional convoy-backup call-in (§6) for this run, for a flat payout bump.
- **"Off the Books"** — cargo is flagged fully illegal for this run regardless of its normal legality tier, increasing threat-zone frequency, for a payout bump and a Leverage-relevant rep flag with whichever faction notices.
- **"No Detours"** — locks the route choice to the most exposed/direct path only, for a payout bump.
- **"Blind Run"** — removes the HUD's forward hazard-preview marker (Module 4 will define what that marker normally shows), for a payout bump.

**Design intent (confirmed):** Stakes conditions are always **opt-in per contract**, never a global toggle, and always diegetically framed (a client asking for a favor, not a menu labeled "Hard Mode") — even though the underlying effect functions like a difficulty toggle, the presentation stays entirely in-fiction. This keeps difficulty scaling consistent with Pillar 4 (diegetic consequences) and gives high-skill players a way to raise stakes on *any* contract — including an early tier-1 job — rather than only being challenged once the campaign's fixed escalation curve (Module 1 §7) catches up to their skill.

**Constraint for Module 4:** every mission should be designed to function with **zero** Special Conditions active — Stakes must always be strictly additive risk for additive reward, never a requirement to hit content parity. This is a hard rule I'd flag now so mission design doesn't accidentally start depending on it.

---

## 4. Mid-Run Agency

Beyond the pre-run loadout, the player retains a small set of live decisions during the drive itself:

- **Route forks:** For contracts designed with an in-drive fork rather than a pre-run route pick, the player commits at the fork itself — no backing out, matching Pillar 1 ("The Road Is the Boss") by making the terrain choice feel like a real driving decision rather than a menu.
- **Leverage use:** For runners with meaningful Leverage (Module 2 §1), a checkpoint or barricade can be talked past instead of run past — costing time (and therefore late-delivery risk) but avoiding a Cargo Integrity or Nerve hit entirely. This is the primary way Leverage cashes out mechanically mid-run rather than only between runs.
- **The Bail:** At any point past the halfway mark of a run, the player can voluntarily abort — pull over, call the client, eat a partial-failure result (reduced but non-zero payout, a smaller rep hit than an actual failure) rather than risk total loss by pushing on with a badly damaged vehicle or heavily degraded cargo. This always costs something, even at low Stakes — no zero-cost bail exists at any difficulty level, so "cut your losses" stays a real trade-off (a legitimate, designed strategy) rather than a free safety net the player can lean on by default.
- **Convoy Backup call-in (optional, cost-bearing):** On contracts where it's offered, the player can call in a single AI-controlled escort vehicle mid-run at a payout cost (deducted from final earnings) — useful against a threat zone, but it raises the run's Profile (more attention drawn, per Module 2 §3's vehicle axis applying to the *run* as a whole while it's active). *Feasibility note (confirmed):* this stays a single additional entity, not a squad, and reuses the same pursuer/escort AI budget Module 1 §6.3 already allocates to threat zones rather than introducing a new entity class — it doesn't add meaningful scope beyond what threat zones need regardless, so it's sound to keep even at a draft/initial build stage.

---

## 5. Difficulty Scaling

Difficulty operates on three independent layers, which should not be conflated in Module 4's mission design:

| Layer | Who controls it | What it scales |
|---|---|---|
| **Campaign Escalation** | Fixed, authored (Module 1 §7) | The tier curve every player experiences in the same order — cargo fragility, terrain, threat zones, composite missions. |
| **Stakes Dial** | Player, per-contract, opt-in (§3) | Extra risk on any individual contract, any tier, for extra payout. Fully reversible contract-to-contract. |
| **Accessibility Presets** | Player, global, session-level | Assist options (traction assist strength, hazard-preview clarity, cargo-damage tolerance banding) that widen or narrow the skill floor without touching payout, narrative, or Stakes availability. These should never be framed as "easy/normal/hard" — accessibility and challenge are different axes and conflating them punishes players who need the assists but still want full Stakes engagement. |

This three-layer split means a new player and a speedrun-minded veteran can both be engaging with tier-1 content productively at the same time — the veteran via Stakes, the newcomer via Accessibility Presets — without either needing the campaign's authored curve to move.

---

## 6. Between-Run Meta-Progression (high-level only — full economy pass is a later document)

Between contracts, the player spends earned payout and reputation on:
- **Vehicle upgrades** — incremental, not power-creep (per Module 2 §3, vehicles stay flat-balanced; upgrades should shift a vehicle's own two-strong/one-weak profile slightly, never erase its weak axis entirely).
- **Roster unlocks** — new runners/vehicles per Module 2 §6, gated by rep/story rather than raw currency.
- **Convoy Backup contracts** — pre-purchased "calls" bankable for future runs, so the mid-run cost (§4) isn't purely a per-run currency drain if the player wants to plan around it.

Full pacing/economy numbers are explicitly out of scope for this module — flagged here only so Module 4 doesn't have to invent an economy from scratch.

---

## 7. Risk/Reward Framework — Summary

| Decision Point | When | Reversible? | Primary Trade-off |
|---|---|---|---|
| Runner + Vehicle | Pre-run | Yes, until commit | Coverage of the contract's specific hazard combination (Module 2 §5) |
| Route (pre-run style) | Pre-run | Yes, until commit | Exposure vs. safety/speed |
| Stakes conditions | Pre-run | Yes, until commit | Payout bonus vs. added risk, fully opt-in |
| Route fork (in-drive style) | Mid-run | No, once past the fork | Same exposure vs. safety trade, but under time pressure |
| Leverage use | Mid-run | No, once used | Time cost vs. avoided integrity/nerve hit |
| Convoy Backup call-in | Mid-run | No, once called | Payout cost + raised Profile vs. threat-zone survivability |
| The Bail | Mid-run | No, once taken | Partial guaranteed payout vs. gambling on a full delivery |

---

## Decisions Log
- **Stakes framing:** Confirmed diegetic (client-offered Special Conditions), never a settings-menu toggle, despite functioning as one mechanically. ✅
- **The Bail's cost:** Confirmed to always sting — no zero-cost bail at any Stakes level, so it never becomes a default safety net. ✅
- **Convoy Backup:** Confirmed in scope. Reuses the threat-zone pursuer AI budget (Module 1 §6.3) rather than adding a new entity class, so it's sound even at a draft/initial build stage. ✅

---

*Next: Module 4 — Mission Design (level objectives, routes, primary hazards, dynamic obstacles, and success/failure conditions).*
