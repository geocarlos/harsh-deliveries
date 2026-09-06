# Module 4: Mission Design

**Status:** Approved — closes out **Version 0** of the design (see Version 0 Close-Out below).

This module defines the mission template every contract is built from, catalogs the hazard/obstacle vocabulary missions draw on, and works through one fully-specified sample mission per escalation tier (Module 1 §7). It's the layer where Modules 1–3's systems (cargo integrity, terrain, threat zones, the Four Levers, Stakes) get applied to concrete level content.

---

## 1. Mission Spec Template

Every mission — hand-authored or, later, generated from a template — should define these fields. This is the checklist Module 5+ (if we get there) or an actual level-design pass would fill in per contract:

| Field | Purpose |
|---|---|
| **Client / Region** | Who's paying, which region-tension faction this contract nudges (Module 1 §4) — omitted for stance-neutral filler contracts, required for story-relevant ones. |
| **Cargo Profile** | Fragility tier + legality flag (Module 1 §6.1) — sets which vehicles/Stakes conditions are even eligible. |
| **Objective** | The delivery goal in plain terms — usually just A→B, but see §2 for objective variants. |
| **Route Structure** | Pre-run discrete choice vs. in-drive fork (Module 3 §2) — and how many meaningful branches. |
| **Primary Hazard(s)** | Which 1–2 hazard categories (§3) headline this mission — a mission should have a clear headline hazard, not an unfocused grab-bag. |
| **Dynamic Obstacles** | Specific instances of §3's catalog placed along the route(s). |
| **Available Stakes Conditions** | Which Special Conditions (Module 3 §3) this contract offers, if any — not every contract needs to offer all of them. |
| **Success / Failure Conditions** | Per §4 below — stated per-mission because thresholds (e.g. cargo integrity floor, time limit) vary by cargo/terrain. |
| **Suggested (not required) Loadout** | One or two Runner+Vehicle pairings the mission was tuned around, for playtesting and for the in-fiction dispatcher hint text — never a hard gate (Pillar 3). |

---

## 2. Objective Variants

Baseline objective is always **A → B, cargo intact, on time**. Three variants recur without becoming new systems:

- **Waypoint delivery:** Multiple drop points in sequence (partial payout per waypoint reached) — used to make the Bail (Module 3 §4) a graded decision rather than all-or-nothing, since a bailed multi-waypoint run still banks whatever was already delivered.
- **Timed extraction:** A fixed, tight time limit replaces the usual "late delivery" soft penalty (Module 1 §5) with a hard fail — reserved for tier 4+ contracts where the client's urgency is itself part of the fiction (e.g. moving something before a checkpoint shift change).
- **No-contact delivery:** Success requires the cargo be delivered without the vehicle ever entering a threat zone's detection radius at all — a stealth-flavored variant that rewards Profile-conscious loadouts (Module 2 §3) and route choice over raw driving skill.

---

## 3. Hazard & Obstacle Catalog

Grouped by the two headline categories from Module 1 §6; each entry is a reusable, nameable unit missions place instances of, not a bespoke one-off.

### 3.1 Terrain Hazards
- **Washout** — a road segment with sharply reduced traction (mud, ice, loose gravel); punishes speed, rewards Terrain Reading.
- **Ridge Line** — a route segment narrow enough that only certain vehicle profiles fit (ties directly to the Wasp, Module 2 §4.5); a wrong line here risks a fall, not just a scrape.
- **Bog Crossing** — a segment where sustained low speed is mandatory or traction fails entirely; the "the Road Is the Boss" hazard that punishes players trying to brute-force a normally speed-rewarded game.
- **Blind Switchback** — a sharp, low-visibility turn placed to punish committing to a route choice at full speed; pairs well with the in-drive fork objective variant.

### 3.2 Threat Zone Hazards
- **Checkpoint** — a static barricade requiring either a Leverage talk-down (Module 3 §4), a forced stop-and-search (cargo-legality-dependent), or a run-the-block risk.
- **Pursuit** — a triggered chase sequence, single-digit pursuer count per Module 1 §6.3, escalating from "shake them on a route feature" (early tiers) to "you cannot outrun this, only out-navigate it" (later tiers).
- **Ambush Point** — a scripted, location-triggered encounter (not a roaming pursuit) — telegraphed just enough that route/loadout choice can preempt it, matching Pillar 4 (consequences should read as earned, not as a gotcha).
- **Hot Zone** — an area-of-effect designation (not a single trigger) where Profile is actively monitored for the duration of transit — the mechanical backbone of the no-contact objective variant and the "Off the Books" Stakes condition (Module 3 §3).

**Composite hazards** (tier 5): mission design should combine one terrain hazard with one threat-zone hazard *at the same location*, not merely in the same level — e.g., a Pursuit that chases the player onto a Ridge Line, so the terrain and the threat pressure compound rather than sit side-by-side. This is the concrete expression of Module 1 §6.5's "additive and combinatorial" escalation principle.

---

## 4. Success / Failure Conditions — General Rubric

Restating and formalizing Module 1 §5's four outcomes with the specific thresholds a mission spec must fill in:

| Outcome | Trigger | Payout | Rep |
|---|---|---|---|
| **Delivered intact** | Cargo integrity above the mission's fragility-defined floor, on time | Full | Full positive |
| **Delivered damaged** | Cargo integrity dropped below floor but cargo not destroyed | Reduced (mission defines the scale) | Reduced positive |
| **Delivered late** | Integrity fine, arrival past time limit (soft) or waypoint schedule | Reduced | Small negative with that client |
| **Bailed** | Player-initiated abort past the midpoint (Module 3 §4) | Partial, scaled to waypoints/distance covered | Small negative, less than Failed |
| **Failed** | Cargo destroyed, vehicle disabled, or (Timed Extraction variant) hard time limit missed | None | Negative, scaled to contract tier |

Every mission spec must state its **fragility floor** (cargo profile-dependent, from Module 1 §6.1) and, if using the Timed Extraction variant, its **hard time limit** — these two numbers are the only thresholds that vary meaningfully per mission; the outcome table itself doesn't change shape.

---

## 5. Sample Missions (one per escalation tier)

These are worked examples to validate the template and hazard catalog — not final shipped content.

### 5.1 Tier 1 — "Dry Goods, Millbrook Road"
- **Client/Region:** Independent grocer, neutral region.
- **Cargo:** Canned goods, low fragility, legal.
- **Objective:** Standard A→B.
- **Route:** Pre-run choice of two paved routes, one longer-but-flat, one shorter with a single Washout.
- **Primary Hazard:** Terrain (Washout) only.
- **Dynamic Obstacles:** One Washout segment.
- **Stakes Offered:** "No Detours" only.
- **Success/Failure:** Fragility floor is generous; no time limit beyond a loose soft-late window.
- **Suggested Loadout:** Any starting Runner + The Mule. Intended as the tutorial-adjacent mission.

### 5.2 Tier 2 — "Glassware, North Corridor"
- **Client/Region:** Small merchant, neutral region.
- **Cargo:** Glassware, high fragility, legal.
- **Objective:** Standard A→B.
- **Route:** Pre-run choice between a rough shortcut (two Washouts) and a smooth long way round.
- **Primary Hazard:** Cargo fragility interacting with terrain — the same Washouts as tier 1, but now the fragility floor is tight enough that route choice actually matters.
- **Dynamic Obstacles:** Two Washouts on the short route, none on the long route.
- **Stakes Offered:** "No Detours" (high risk here specifically, since it removes the safe long route).
- **Suggested Loadout:** Diego (Cargo Care) or Mara (Cargo Care) + The Mule.

### 5.3 Tier 3 — "The Pass, Highland Corridor"
- **Client/Region:** Iveta's home region client — regional de-escalation flavor available per her stance (Module 2 §2.4).
- **Cargo:** Machine parts, medium fragility, legal.
- **Objective:** Standard A→B.
- **Route:** In-drive fork (not pre-run) — a Blind Switchback partway through commits the player to either the Ridge Line (fast, narrow, vehicle-profile-gated) or a longer Bog Crossing.
- **Primary Hazard:** Terrain (Ridge Line / Bog Crossing as alternatives).
- **Dynamic Obstacles:** One Blind Switchback fork, one Ridge Line, one Bog Crossing.
- **Stakes Offered:** "Blind Run" (removes hazard-preview, meaningfully harder given the blind fork already present).
- **Suggested Loadout:** Iveta + The Goat (if taking the Bog) or Iveta + The Wasp (if taking the Ridge) — this mission is the clearest demonstration of Module 2 §5's "unlocks a route other loadouts can't attempt" design intent, since The Wasp is the only vehicle that comfortably clears the Ridge Line here.

### 5.4 Tier 4 — "Off the Manifest, Dockside"
- **Client/Region:** Unnamed broker, a region currently trending toward militarization.
- **Cargo:** Undeclared cargo, low physical fragility but fully illegal.
- **Objective:** No-contact delivery variant.
- **Route:** Pre-run choice of two routes, both passing near a Hot Zone at different distances.
- **Primary Hazard:** Threat zone (Hot Zone + a scripted Ambush Point on the closer route).
- **Dynamic Obstacles:** One Hot Zone, one Ambush Point, one Checkpoint (talk-down eligible) on the farther/safer route.
- **Stakes Offered:** "Off the Books" (redundant here since cargo is already illegal — mission spec should instead offer "No Escort Frequency" to keep Stakes meaningful).
- **Suggested Loadout:** Kass (Nerve) + The Needle (Profile) for the close route; Mara (Leverage) + The Mule for the checkpoint talk-down route.

### 5.5 Tier 5 — "Full Manifest, Composite Run" (region-tension-relevant, late campaign)
- **Client/Region:** Player's choice at dispatch — same cargo offered by both a destabilizing-faction client and a de-escalation-aligned client, at different payouts (the concrete instance of Module 1 §4's routing choice).
- **Cargo:** Volatile chemical drums, high fragility, illegal.
- **Objective:** Timed extraction variant (a checkpoint shift-change window).
- **Route:** In-drive fork mid-run: a Pursuit triggers approaching a Ridge Line, forcing the composite-hazard interaction described in §3's closing note — the pursuers don't stop chasing just because the road got narrow.
- **Primary Hazards:** Terrain (Ridge Line) + Threat zone (Pursuit), compounding at the same location, plus the cargo's own fragility making every evasive maneuver costly.
- **Dynamic Obstacles:** One Pursuit trigger timed to reach the player at the Ridge Line, one Checkpoint before the fork (talk-down optional), hard time limit from the Timed Extraction objective.
- **Stakes Offered:** "Blind Run" and "No Escort Frequency" both available — this is a mission built to showcase Convoy Backup's value proposition by making it genuinely tempting to spend the payout on it.
- **Suggested Loadout:** The Warden (Cargo Care + Nerve, Module 2 §2.6) is the first loadout in the game that can take this mission without a glaring weak axis — intentional, since the Warden unlocks around this point in the region-tension arc.

---

## 6. Design Notes for Future Mission Authoring

- Every mission must have a **headline hazard** (§1) — resist the urge to stack every hazard type into every tier-5+ mission; composite means *two* hazards compounding at one location, not five hazards scattered across a level.
- **Route choice must always be legible before commit** for pre-run route missions (per Pillar 4) — an in-drive fork is the only place hiding information (via "Blind Run" Stakes) is acceptable, and only because the player opted into that specifically.
- Reuse catalog entries (§3) rather than inventing new named hazards per mission — the catalog is deliberately small so hazard combinations, not hazard variety, drive difficulty and content volume.

---

## Decisions Log
- **Region-tension client choice (5.5):** Confirmed — same cargo offered by two opposing-faction clients at different payouts is the standard mechanical surface for region-tension routing, at the dispatch board. ✅
- **Timed Extraction's hard fail:** Confirmed as designed — a true fail state on a missed window, kept deliberately harder-edged than the normal late-delivery model, and deliberately reserved for tier 4+ story-relevant contracts rather than used broadly. ✅
- **Mission count per tier:** Confirmed — the five tier samples validate the template and are sufficient for Version 0. A larger per-tier batch (3–5 missions each) is deferred to a dedicated level-design pass once implementation and asset production are further along, rather than authored speculatively now. ✅

---

## Version 0 Close-Out

This closes the four responsibility areas from the original brief — Narrative & World Design (Module 1), Character & Vehicle Design (Module 2), Gameplay & Player Agency (Module 3), and Mission Design (this module) — as **Version 0** of Harsh Deliveries' game design. Per your direction, design work pauses here; the project moves to asset design/creation next, then implementation against these four documents, then a revisit pass once a basic playable build exists.

A few notes and one recommendation, flagged now so they don't get lost during a long asset-production phase where no one may be re-reading these documents day-to-day:

- **Nothing here is a fixed number.** Fragility floors, payout scales, pursuer counts, Stakes payout bonuses, and similar figures are described qualitatively/relatively on purpose — they're deliberately left untuned pending actual play. Whoever picks up implementation should expect to playtest and adjust these rather than treat any number in these four docs as final.
- **Cross-module dependencies to watch:** the Warden's unlock condition (Module 2 §2.6) and the region-tension client-choice mechanic (this module, §5.5) both depend on a persistent, cross-runner world-state (Module 1 §4) surviving between contracts. That's a design requirement worth flagging early to whoever architects state/save systems, since it's load-bearing for two separate pieces of content, not a minor flourish.
- **Production recommendation (yours to weigh, not a blocker):** given asset creation is expected to be a long run, I'd suggest sequencing a small **vertical slice** first — one or two runners, one or two vehicles, and the Tier 1 and Tier 3 sample missions (§5.1, §5.3) specifically, since between them they exercise cargo integrity, terrain hazard, and the in-drive-fork route system without needing threat-zone AI or the full roster — before committing art/asset budget to the entire six-runner, five-vehicle, five-tier scope. That validates the pipeline and the core loop's feel cheaply before the expensive part (threat-zone content, the full roster, region-tension state plumbing) gets built out. Purely a sequencing suggestion — doesn't change any design decision made in these four documents.
- **When you revisit:** treat these four files as the Version 0 baseline to diff against, not to rewrite in place — if playtesting the basic build reveals a mechanic doesn't work as designed, I'd suggest a short "Version 0.1 addendum" noting what changed and why, rather than silently editing history, so the reasoning trail (a lot of which is *why* a decision was made, not just what) stays intact.

*No further modules planned until the revisit pass. This document set (Modules 1–4) is the complete Version 0 design.*
