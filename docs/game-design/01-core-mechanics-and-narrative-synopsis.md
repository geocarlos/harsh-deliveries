# Module 1: Core Mechanics & High-Concept Narrative Synopsis

**Status:** Approved — customizable roster, region-tension moral framing, and tone confirmed by producer. Proceeding to Module 2 (Character & Vehicle Design).

## Working Title
**HARSH DELIVERIES**

## Logline
*In a world where trust is currency and roads are battlefields, you're the only thing standing between "the package" and everyone who wants it gone, exposed, or stolen — deliver it anyway.*

---

## 1. High-Concept Pitch

Harsh Deliveries is a **vehicle-based delivery roguelite-lite**: every contract is a self-contained gauntlet — pick your driver, pick your vehicle, pick your route, and get an item from Point A to Point B before terrain, weather, cargo fragility, or armed opposition takes it from you first. There is no combat-for-its-own-sake and no open-world grinding. The game is built entirely around **one question repeated with escalating stakes**: *how much risk are you willing to carry to get paid?*

The player never fights *to win* — they fight (or flee, or bribe, or bluff) *to keep driving*. Every system in the game exists to put pressure on the drive itself.

### Design Pillars
1. **The Road Is the Boss.** Terrain and environmental hazards are the primary antagonist in early-to-mid game — human threats are seasoning added later, never a replacement.
2. **Cargo Has Opinions.** What you're hauling constrains *how* you're allowed to drive it. A crate of stable canned goods and a case of unstable chemical drums demand entirely different driving disciplines, even on an identical route.
3. **Every Route Is a Negotiation.** The player always chooses between the safe-slow path and the fast-exposed path. No route is ever strictly correct — only correct for the cargo, the vehicle, and the player's nerve that run.
4. **Consequences Are Diegetic, Not UI.** Failure states (spilled cargo, a cracked vehicle frame, a blown reputation) should read as things that happened in the world, not a health bar hitting zero.

---

## 2. World Primer

**Setting:** A near-future federation of fractured territories — think a continent stitched together after a long economic collapse, where legitimate freight infrastructure died and an unregulated "gray logistics" economy rose to fill the gap. No single government controls the roads; instead, a patchwork of corporate checkpoints, regional militias, opportunist gangs, and desperate small towns all depend on **runners** — independent drivers who move what the broken system can't or won't.

**Tone:** Grounded, tense, darkly funny in the margins (radio chatter, dispatcher banter, roadside graffiti) but never flippant about the danger. Think *Death Stranding*'s delivery-as-lifeline stakes crossed with *Death Proof* / *Mad Max* vehicular tension and the moral murk of a smuggling story — you will, at some point, be asked to move something you don't feel great about, for a price you can't refuse.

---

## 3. Protagonist Framing: The Runner Roster

**Decision (confirmed):** There is no single fixed protagonist. The player chooses from a roster of distinct, pre-authored runners — each with their own personality, backstory fragment, and mechanical driving identity (detailed per-character in Module 2). The avatar is *customizable by selection*, not by silent-avatar creation: every runner is a written character, but the player picks who they are for a given campaign or contract.

This reframes the overarching story spine below: it is not one person's arc, but **a shared world-state** that every runner is enmeshed in. Whichever runner the player is driving as, the same faction pressures, the same regional consequences, and the same "buy your way out" throughline apply — the roster changes *whose eyes* the story is told through and *how* they personally relate to the job (a debt-runner sees a contract differently than an idealist-runner or a mercenary-runner), not *what* the story is.

**Implication for later modules:**
- Module 2 will define each runner as a distinct combination of personality, motivation, moral alignment, and driving traits (strengths/weaknesses) — not reskins of the same stats.
- Dispatcher/NPC dialogue should be written with light branch-awareness (a line or two of reaction) to whichever runner is active, without requiring a fully separate script per character.
- The region-tension world-state (below) persists **across runners** — it belongs to the world, not to an individual's save file — so switching who you play as does not reset the consequences of prior deliveries.

---

## 4. The Overarching Story: Region Tension, Not a Morality Meter

**The Throughline:** Every runner in the roster is, in their own way, trying to buy their way out — out of debt, out of a territory, out of the life. Every contract accepted is framed as "one step closer to out." The campaign's spine is a slow-burn discovery that the biggest, best-paying clients (the ones offering the jobs that finally make "out" possible) are the same factions responsible for why the roads got this dangerous in the first place.

**Confirmed framing:** The player is never forced into a binary morality choice. Instead, from the mid-game onward, contracts increasingly offer a *routing* choice baked into normal dispatch-board decisions: fulfill the job for the faction that stands to further militarize/destabilize a region, or route the same (or an equivalent) contract toward a client whose success calms that region down. This is presented as a logistics/payout trade-off first, a moral one second — the player is always free to optimize for money and let the tension resolve itself as a byproduct.

**World-state consequence:** Regional danger (checkpoint density, patrol aggression, ambient hazard-zone frequency) shifts visibly over the campaign as an *accumulated result* of many small contract choices, not a single ending-branch decision. This should read environmentally — signage, wreckage, roadside chatter, dispatch-board contract mix changing per region — rather than through a stat screen.

**Why this framing (confirmed rationale):** It keeps the moral weight *diegetic and cumulative*, matching Pillar 4 ("Consequences Are Diegetic, Not UI") — the player feels the weight of a choice through the world reacting, not through being told they made a good or bad choice.

---

## 5. Core Gameplay Loop

```
DISPATCH BOARD → CONTRACT SELECT → LOADOUT (Runner + Vehicle + Route) → THE DRIVE → DELIVERY OUTCOME → PAYOUT/REP → back to Dispatch Board
```

**Dispatch Board:** Contracts are listed with legibility up front, not mystery-box surprise — cargo type, known route hazards, payout, and a risk rating. Player skill is expressed in *reading* a contract correctly, not in memorizing hidden gotchas.

**Loadout:** The moment of build-crafting. Runner + Vehicle + Route form a triangle where two strong choices can offset one weak one (e.g., a fragile vehicle paired with a runner whose specialty is smooth handling, taking the longer-but-flatter route).

**The Drive:** The core 3–12 minute play session. This is where all runtime mechanics below fire simultaneously.

**Delivery Outcome:** Binary-adjacent but not binary — "delivered intact," "delivered damaged" (reduced payout), "delivered late" (reduced payout + rep hit with that client), or "failed" (cargo lost/destroyed, rep hit, possible debt). Partial success is core to the loop — this isn't a fail-and-retry game, it's a *how much did it cost you* game.

**Payout/Rep:** Money buys vehicle upgrades and unlocks; Reputation (per-faction) gates which contracts appear and colors the region-tension world-state above.

---

## 6. Core Runtime Mechanics (Design Intent + Engine-Feasibility Notes)

Feasibility notes are here to make sure the design doesn't write checks the Babylon.js runtime can't cash — these are constraints on scope, not implementation specs.

### 6.1 Cargo Integrity
Cargo is not a health bar — it's a **physical state driven by how the vehicle is driven.** Hard impacts, sustained high-speed vibration over rough terrain, and sharp direction changes all contribute to a hidden-but-fair-feeling integrity value. Different cargo types have different tolerance curves (a sealed steel drum shrugs off bumps a crate of glassware would not).
- *Feasibility:* Readable from vehicle physics values the engine already tracks (impulse magnitude, suspension compression) rather than requiring bespoke per-cargo simulation. Cargo "profiles" are tolerance curves against those existing signals, not new physics systems.

### 6.2 Terrain & Environmental Hazard
Mountains, swamps, and narrow ridges aren't set-dressing — they're the primary difficulty lever pre-threat-zone content. Terrain hazard is expressed through traction loss, verticality/fall risk, and route width forcing commitment (no correcting a bad line on a one-lane ridge).
- *Feasibility:* Hazard density built around discrete, moderate-count trigger volumes and terrain material zones rather than dense continuous destructible terrain — keeps this achievable within a web physics budget.

### 6.3 Threat Zones (Human Opposition)
Introduced in escalation tier 2+. Police chases, gang ambushes, and barricades are **pressure generators, not combat encounters** — their job is to force bad driving decisions (speeding through terrain you shouldn't, taking the exposed route) rather than to be fought head-on. The player's default tool against a threat zone is *route and speed*, not weapons.
- *Feasibility:* Encounters designed as a handful of active pursuer/obstacle entities per zone (single digits, not swarms) with scripted spawn/despawn at zone boundaries — keeps active entity counts sane for a web-target engine.

### 6.4 Risk/Reward Routing
Every contract route offers at least two paths differing in exposure vs. speed/safety. This isn't a fork with one correct answer — it's a re-askable question every contract, because the "right" answer changes with cargo fragility and vehicle choice, and (from mid-game on) with which region-tension outcome the player wants to nudge.

### 6.5 Difficulty Scaling
Escalation is **additive and combinatorial**, not just "bigger numbers": simple cargo → fragile/unstable cargo → extreme terrain → terrain + fragile cargo → illegal cargo + threat zones → all-hazard composite levels. Difficulty comes from stacking known systems in new combinations, not introducing unexplained new ones late.

---

## 7. Escalation Curve (High-Level Only — full mission specs come in a later module)

| Tier | Introduces | Player Question Being Asked |
|---|---|---|
| 1 | Basic cargo, basic roads | "Can you drive competently?" |
| 2 | Fragile/unstable cargo | "Can you drive *carefully*?" |
| 3 | Extreme geography (mountains, swamps, ridges) | "Can you read terrain under pressure?" |
| 4 | Illegal cargo + active threat zones (chases, ambushes, barricades) | "Can you handle being hunted?" |
| 5 | Composite (all of the above, simultaneously) + region-tension routing choices become available | "Can you hold it together — and whose interests are you actually serving — when everything is asking something of you at once?" |

---

## Decisions Log
- **Protagonist:** Roster of distinct, pre-written selectable runners (not a fixed hero, not a silent create-a-character avatar). ✅
- **Moral framing:** Region-tension routing choice (de-escalate vs. chase highest bidder), diegetic and cumulative, not a morality meter. ✅
- **Tone:** Grounded/tense with margin humor, confirmed. ✅
- **Deliverables location:** `docs/game-design/` — this file is the first deliverable of that folder.

---

*Next: Module 2 — Character & Vehicle Design (full runner roster, vehicle roster, driving-trait design).*
