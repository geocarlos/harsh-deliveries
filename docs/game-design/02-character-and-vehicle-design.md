# Module 2: Character & Vehicle Design

**Status:** Approved — 6th wildcard runner slot, Iveta's regional stance, and the Bastion's role all confirmed by producer. Proceeding to Module 3 (Gameplay & Player Agency).

This module delivers the **Runner Roster** (playable characters) and the **Vehicle Roster**, plus the framework for how the two combine. Per [Module 1](01-core-mechanics-and-narrative-synopsis.md), there is no single fixed protagonist — the player selects from a cast of distinct, pre-authored runners, and the region-tension world-state belongs to the world, not to whichever runner is currently active.

---

## 1. Runner Design Framework

Every runner is defined along five qualitative axes. These are design-level descriptors (for writing and balancing purposes), not a spec for how they're stored or computed at runtime:

| Axis | What it governs in play |
|---|---|
| **Handling** | How forgiving the vehicle feels under this runner's control — correction speed after a slide, composure on tight lines. |
| **Cargo Care** | How much a given driving mistake (hard impact, sharp swerve) actually costs the cargo — some runners drive "softer" by instinct. |
| **Nerve** | Composure inside a threat zone — how much a pursuit or ambush degrades this runner's driving versus sharpening it. |
| **Terrain Reading** | Skill on mountains/swamps/ridges specifically — reading a bad line before committing to it. |
| **Leverage** | Non-driving social capital — ability to talk down a barricade, haggle a payout, or get a faction to look the other way. |

No runner is best at everything — every runner is strong on two axes, weak on one, and average on the rest. This is the same design contract as vehicles (Section 3) so that Runner + Vehicle pairing is always a real trade-off, per Pillar 3 ("Every Route Is a Negotiation") extended to loadout itself.

Each runner also carries a **stance** on the region-tension spine (Module 1, Section 4) — not a locked morality flag, but a default lean in how their dispatcher dialogue frames a contract. The player can still route any runner's contracts either way; the stance colors *how the choice is presented and voiced*, not what's mechanically available.

---

## 2. Runner Roster

### 2.1 Mara Itoh — "The Ledger"
**Hook:** Owes the wrong bank. Drives like every scratch on the vehicle is a line item she'll have to explain.
**Personality:** Precise, dry, keeps a running mental tally of everything — money, favors, damage. Not cold, just allergic to surprises.
**Motivation:** Pay off a debt to a logistics cartel that's actually one of the region-destabilizing factions — she knows exactly whose money she's taking and hates it.
**Stance:** Pragmatist. Defaults to highest bidder, but is the character best positioned to *notice* and comment on the region-tension pattern first — she's the one doing the math on who's paying whom.
**Driving Traits:** Strong **Cargo Care**, strong **Leverage** (talks numbers, not threats). Weak **Nerve** — she is not built for being shot at and it shows in her driving under pursuit.

### 2.2 Diego Salvatierra — "Padre"
**Hook:** Ex-field medic who now runs medical and aid cargo through territory the aid agencies won't enter.
**Personality:** Warm, direct, quietly furious at the state of things. Talks to cargo like it's a patient.
**Motivation:** Genuinely wants regions to calm down — not an abstract ideal, he's seen what the alternative costs.
**Stance:** Idealist. Defaults to de-escalation contracts when offered a choice; dispatcher dialogue will occasionally push back at him for taking a lower payout on principle.
**Driving Traits:** Strong **Cargo Care**, strong **Terrain Reading** (learned back roads moving aid through blockaded zones). Weak **Nerve** — he freezes for a half-beat the first time a threat zone escalates each run, a small but real cost.

### 2.3 Kass Ferreira — "Kass"
**Hook:** Ex-military, does this because it's the only adrenaline left that pays. Doesn't ask what's in the crate.
**Personality:** Clipped, funny in a bleak way, treats every ambush like a tactical puzzle rather than a threat.
**Motivation:** Money and the rush — currently the character with the least invested in the region-tension spine, which is itself the point: she's the "what if you just don't care" option, and the story lets that be a valid, un-punished way to play.
**Stance:** Mercenary. No default lean; dispatcher dialogue treats every contract as equally transactional, which some players will find refreshing.
**Driving Traits:** Strong **Nerve**, strong **Handling** under pressure. Weak **Cargo Care** — she drives to win the encounter, not to protect the crate, and it costs fragile-cargo contracts.

### 2.4 Iveta Rusul — "Highland"
**Hook:** Grew up in the mountain corridor territories before the roads got dangerous; still knows every washout and goat track.
**Personality:** Quiet, blunt, mistrustful of corporate clients, warm with locals.
**Motivation:** Protect her home region specifically — she has personal, place-based stakes rather than an abstract stance on the whole map.
**Stance:** Idealist, but *localized* — she'll route hard toward de-escalation in her home region and stay neutral-to-mercenary everywhere else, which gives dispatcher dialogue a distinct regional flavor.
**Driving Traits:** Strong **Terrain Reading**, strong **Handling** off-road. Weak **Leverage** — she has no patience for corporate checkpoint theater and it shows; talk-downs go worse for her.

### 2.5 Ren Okafor-Boyle — "Wire"
**Hook:** Youngest runner on the board, reckless, treats the job as a highlight reel. Everyone's worried about him, including his dispatcher.
**Personality:** Fast-talking, overconfident, genuinely funny — the game's main source of margin humor is Wire's radio chatter.
**Motivation:** Reputation and speed records among the runner community; money is secondary, which makes him take contracts others turn down out of sheer bravado.
**Stance:** Undeclared/mercurial — Wire doesn't have a stance yet, and late-game dialogue can use this: Wire is the character most reactive to *what the player has already done* with other runners, since he looks up to whoever's actually getting results.
**Driving Traits:** Strong **Handling**, strong **Nerve** (bravado reads as composure right up until it doesn't). Weak **Cargo Care** — the single highest cargo-damage-variance runner in the roster, by design: high skill ceiling, high floor risk.

### 2.6 [Wildcard] — "The Warden"
**Slot type:** 6th roster runner, unlocked late-campaign rather than sold or found — availability is gated by the accumulated region-tension world-state (Module 1 §4) crossing a threshold, in either direction, rather than by payout or a fixed story beat. The Warden is a payoff for having *played the region-tension spine long enough to move it*, not a raw endgame reward.
**Hook:** Former enforcer for one of the region-destabilizing factions, now running cargo for reasons the game lets stay ambiguous rather than spelling out as clean redemption.
**Personality:** Guarded, economical with words, unnervingly calm — reads as either "seen worse than this" or "still expects worse than this," and which reading lands harder depends on how the player's own runs have gone.
**Motivation:** Unstated by design — the Warden's dispatcher barks are written with two flavor variants (calmed-world vs. still-militarized-world at time of unlock) rather than a fixed backstory reveal, so the character reflects the state the player actually produced rather than a single scripted arc.
**Stance:** None declared — the Warden is the one runner who never comments on a contract's region-tension framing either way, which is itself the character's voice.
**Driving Traits:** Strong **Cargo Care** *and* strong **Nerve** — the one deliberate exception to the roster balance rule below, earned rather than starting-available, giving late-game players their first clean answer to fragile-cargo-under-fire tier-5 contracts. Weak **Handling** — never formally trained as a driver, learned everything under live fire, and it still shows in how the vehicle corrects.

**Roster balance note:** Among the five starting runners, no one is strong in **Terrain Reading + Nerve** simultaneously, and no one is strong in **Cargo Care + Nerve** simultaneously — those two-axis gaps are intentional, so that tier 5 composite missions (terrain + threat zone + fragile cargo, per Module 1 §7) never have a single "correct" starting runner and always force a Runner+Vehicle compensation choice. The Warden (2.6) is the sole, deliberate exception to the Cargo Care+Nerve gap — the wildcard slot exists specifically to eventually break one rule the base roster holds, once the player has earned it.

---

## 3. Vehicle Design Framework

Vehicles are defined along a parallel set of axes so they can compensate for (or compound) a runner's weaknesses:

| Axis | What it governs in play |
|---|---|
| **Durability** | How much raw physical punishment the vehicle absorbs before the *vehicle itself* is at risk (separate from cargo). |
| **Cargo Care** | The vehicle's own baseline harshness — suspension and bed design independent of who's driving. |
| **Terrain Traction** | Off-road/rough-surface capability. |
| **Profile** | How exposed/conspicuous the vehicle is — a factor at checkpoints and in threat zones (a loud armored truck draws attention a plain van doesn't). |
| **Capacity** | How much and what size/class of cargo it can take, gating which contracts it's even eligible for. |

Same contract as runners: strong on two, weak on one, average elsewhere. No vehicle is a strict upgrade over another — progression unlocks *breadth of options*, not a power ladder (kept deliberately flat so early-roster vehicles stay relevant late, matching Pillar 3).

---

## 4. Vehicle Roster

### 4.1 The Mule (cargo van)
Strong **Cargo Care**, strong **Capacity**. Weak **Terrain Traction** — road-bound, punished hard off-pavement. The default "learn the game" vehicle; low ceiling, very low floor-risk.

### 4.2 The Goat (off-road pickup)
Strong **Terrain Traction**, strong **Durability**. Weak **Profile** — loud, conspicuous, bad for illegal-cargo/low-visibility contracts. The mountain/swamp specialist vehicle.

### 4.3 The Needle (unmarked sedan)
Strong **Profile** (low visibility, blends into normal traffic) and strong straight-line road performance. Weak **Capacity** — small trunk, gates it out of bulk contracts entirely. The illegal/small-package specialist.

### 4.4 The Bastion (armored transport)
Strong **Durability**, strong **Capacity**. Weak **Cargo Care** — heavy suspension built for surviving hits, not for babying fragile freight; also weak **Profile** (impossible to hide, telegraphs "valuable cargo" to every threat actor on the route). The threat-zone specialist that actively fights the fragile-cargo mechanics.

### 4.5 The Wasp (cargo motorcycle w/ sidecar hauler)
Strong **Terrain Traction** on narrow lines (ridges, single-lane paths nothing else fits through) and strong Profile (small, easy to miss). Weak **Durability** and weak **Capacity** — tiny hauler, and a single hard hit risks totaling both bike and cargo. The high-skill-ceiling niche pick for narrow-ridge and stealth-illegal contracts specifically.

**Roster balance note:** Exactly one vehicle (the Bastion) is strong on Durability+Capacity and weak on both Cargo Care and Profile — this is the deliberate "brings its own new problems" pick, so it's a genuine trade rather than a strict answer to threat-zone tiers.

---

## 5. Runner × Vehicle Synergy — Worked Examples

This is the design contract in action, not new mechanics:

- **Diego + The Goat:** Terrain Reading (runner) + Terrain Traction (vehicle) stack — this pairing trivializes tier-3 pure-terrain contracts, which is fine, because both are weak where it matters (Diego's Nerve, the Goat's Profile) the moment a tier-4 threat zone or illegal-cargo contract shows up.
- **Kass + The Bastion:** Nerve (runner) offsets the Bastion's exposure problem in a threat zone, but neither compensates for the Bastion's poor Cargo Care — this pairing is built to eat fragile-cargo-plus-threat-zone tier-5 missions and nothing else particularly well.
- **Ren ("Wire") + The Needle:** Two "fast and exposed" profiles stacking — high reward on illegal-cargo speed-run contracts, but the pairing has no terrain answer and no durability cushion at all. Highest variance combination in the roster by design.
- **Iveta + The Wasp:** The narrow-ridge specialist pairing — nothing else in the roster can take some ridge routes at all; this is intentionally the "unlocks a route other loadouts can't attempt," not just "does it better."

This confirms the loadout triangle from Module 1 §5 is doing real work: **Runner + Vehicle + Route** should be designed together per-contract in Module 3, not treated as independent menus.

---

## 6. Roster Expansion (high-level only)

New runners and vehicles unlock through reputation and story progression rather than raw payout — keeps unlocks tied to the region-tension spine instead of being a pure grind reward. I'd suggest each new unlock be justified narratively by *something that happened* to a region (a calmed region opens up a local specialist runner or vehicle native to it; a militarized region locks certain low-profile options out until it calms down). Full unlock pacing belongs in a later economy/progression pass, not this module — flagging it here so it isn't forgotten.

---

## Decisions Log
- **Roster size:** Five starting runners + one wildcard slot (2.6, "The Warden") unlocked via accumulated region-tension world-state; five starting vehicles, no wildcard vehicle slot. ✅
- **Iveta's stance:** Kept as a regional (not map-wide) moral lean — an intentional exception that gives her dispatcher dialogue distinct local flavor. ✅
- **The Bastion's role:** Confirmed as a vehicle that actively fights the fragile-cargo system rather than a clean trade-off, and Module 3 should design around that friction rather than smooth it over. ✅

---

*Next: Module 3 — Gameplay & Player Agency (playable choices, customizable settings, difficulty scaling, vehicle select, risk/reward trade-offs per delivery mission).*
