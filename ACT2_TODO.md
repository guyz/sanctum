# Act 2 "The Sunscar Reaches" — State & TODO (handoff)

Single source of truth for what Act 2 **has**, what's **not built**, and the **open bug** the owner wants
fixed by a fresh agent. Everything Act-2 is in the one file `sanctum-of-ash.html` (~31MB; game JS is in
`<script id="game">`; huge base64 lines — always grep length-filtered: `awk 'length($0)<300 && /X/{print NR": "$0}'`).

## How it's gated / how to run
- **All Act 2 is DEV-only**, behind `FEAT.act2 = DEV_BUILD`. `CHANNEL='dev'` only on localhost with `?dev`
  (or native `setup-ios.sh dev`). Public/prod ships `window.__CHANNEL='prod'` → none of this builds. Prod is clean.
- Run/test: `localhost:8841/sanctum-of-ash.html?dev` → CONTINUE/NEW GAME → the desert is Act 2.
- Build stamp prints to console + (touch builds) the title footer: `window.__BUILD`. **Confirm the stamp
  before judging a bug — stale browser/native bundles have repeatedly masked fixes.**
- Save-safe rule: additive fields only, never bump `v` (2) or `questV` (7). Web/desktop path untouched.

---

## ✅ WHAT ACT 2 CURRENTLY HAS (built + committed on `main`)

**Zones** (registry ~line 13160; builders are `buildOasisTown`, `buildSunscar`, `buildTomb`, `buildSunTemple`):
- **Sun's Rest** (`act2town`) — oasis hub; adobe (flat-roof) houses, spaced with streets, NPCs, the
  questgiver **Warden Khenra**, market/well/bonfire. (Reworked from the old cramped medieval look.)
- **The Sunscar Dunes** (`sunscar`) — the open world. **Now R=215 (~30% bigger than Act 1's `OVERWORLD_R`=165).**
  Real terrain heightfield, gates spread to compass edges (S=home, N=Tomb, W=Sun Temple, E=Rift), 4 oases,
  8 landmark mesas baked into the terrain, ~3× foliage density, 6 shrines / 12 chests.
- **The Buried Tomb** (`tomb`) — sandstone dungeon, boss **KHA'ZRUK**.
- **The Sun Temple** (`suntemple`) — light-the-4-seals puzzle, boss **RA-SETH**.
- **The Sunscar Rift** (`rift`) — endless procedural rooms-and-corridors; 10 theme kits; set-pieces
  (boss/vault/altar/locked-door+key); collect-3-shards "Sun-Dial" quest; descend loop with per-floor omen.

**Landmarks (POI beacons in `sunscar`)**: Sunken Colossus (-50,-95), Raider Camp (+captain) (125,-125),
Bone Field (+Bone Tyrant) (-135,120), Ruined Watchtower (95,115). Named elite encounters spawn at the
camp and bone field on entry.

**Mobs** (`ENEMY_TYPES`): Act-1 tinted reskins PLUS 9 distinct-silhouette desert creatures —
`sandcactus, dunelizard, sandhornet, sunmaw, sporeling, sunifrit, dunebehemoth, bonetyrant, dunewyvern`
(+ bosses tombboss/cisternboss/templeboss/mirageboss/strongboss/arenaboss). Wired into dunes/tomb/temple
mixes + 6 rift kits.

**Quests** (`if (FEAT.act2) QUESTS.push(...)`, ~line 18615) — **only 4** (the Warden line):
`Sand in the Wells` (sunscar) → `The Buried King` (tomb) → `The Sealed Light` (suntemple) → `Trial of the Rift`.

**Other (global, but relevant)**: a Lv-20 **Masteries** tier (Spirit Wolf / Sun Totem / Aegis Ward),
DEV-gated `FEAT.masteries`. Town-portal recall + CONTINUE now return to the correct act (act2town).
Cloud sync / Sign in with Apple is wired for the native build (separate from Act 2).

---

## 🔴 OPEN BUG #1 (TOP PRIORITY) — "walking into / through mountains" in Act 2 — NOT FIXED

The owner reports that in Act 2 the player still **walks into mountains / elevated terrain**. This has been
attempted ~10 times and the owner still sees it on their device — **treat it as UNRESOLVED**. Do not assume
the prior approach worked.

**What was tried (all on `sunscar`):**
1. Per-object cylinder colliders on mesh "mesas", collider-radius tweaks, player Y-offsets, sand color/contrast.
2. Final approach (current code): replaced the flat ground + mesh-mountains with a **terrain heightfield** —
   `buildSunscarTerrain()` (~line 14734) builds `sunscarGrid`; `sampleSunscar(x,z)` (~14759) samples it;
   `groundY(x,z)` (~14711) returns it for `sunscar`; the displaced ground mesh is in `buildSunscar` (~15422);
   the perimeter "mountains" are a rim band in the heightfield; the player is kept in by the **`WORLD_R`
   clamp** in `resolveCollisions()` (grep `dc > WORLD_R`). Every entity rides `groundY` per frame.

**Why it may still be wrong (hypotheses for the next agent — verify on a REAL device, not just headless):**
- **Definition mismatch:** a heightfield makes hills/mesas **walk-OVER** (you climb them), it does NOT make
  them solid. If "walking into mountains" means the owner expects mountains to be **impassable walls**, the
  current design is wrong by intent — they'd want solid colliders or much steeper/blocking terrain, not a
  ride-over heightfield.
- **The rim isn't a real wall:** the only thing stopping you at the edge is the circular `WORLD_R` clamp,
  not the visible mountains. If the visual rim and the clamp radius don't line up, you appear to walk into
  the mountain before an invisible wall stops you (or you stop in mid-slope).
- **Stale build:** the owner has repeatedly been on cached browser / old native bundles. **First step:
  confirm the on-device `window.__BUILD` matches the latest commit** before debugging anything.
- **Other zones:** `act2town` is a flat town and `tomb`/`suntemple` are flat-floor dungeons with wall
  colliders — if the complaint is in one of those, the fix is different (prop colliders, not terrain).
- The owner says **Act 1's overworld "works perfectly"** — the canonical reference is `buildTerrain`/
  `sampleTerrain` + how the overworld blocks the player. Diff Act 1 vs Act 2 collision behavior directly.

**Suggested next step:** sit with the owner (or a device) to pin down EXACTLY where and what "walking into
mountains" means (which zone, the perimeter rim vs a mid-map mesa, walk-through vs walk-into-then-stop),
reproduce it live, then decide between (a) align the rim visual with the `WORLD_R` clamp, (b) add a hard
collision wall at the rim, or (c) make mid-map mountains solid props with full-size colliders.

Anchors: `groundY` ~14711 · `buildSunscarTerrain` ~14734 · `sampleSunscar` ~14759 · ground mesh in
`buildSunscar` ~15422 · `WORLD_R` set in `setZone` (grep `WORLD_R = z.r`) · clamp in `resolveCollisions`
(grep `dc > WORLD_R`) · `OVERWORLD_R`/`DUNGEON_R` ~12776.

---

## 🟡 NOT BUILT YET (TODO)

1. **Multi-stage Act 2 storyline** — the biggest gap. Only 4 quests exist; there's no coherent end-to-end
   story, and quest variety is thin (mostly fetch/boss). Proposed (not built) 6-stage Warden arc:
   - Sand in the Wells (clear/intro) → The Caravan's Bones (investigate→escort, uses Raider Camp) →
     The Buried King (Tomb boss) → Shards of the Sun-Dial (collect-and-assemble from Colossus/Bone Field/
     Watchtower) → The Sealed Light (Sun Temple puzzle + RA-SETH) → The Storm-Eater (survive-waves finale,
     then Rift opens as endless endgame).
   - Implement as additive `QUESTS.push` + pictogram trackers; tie quests to the existing landmarks/dungeons.
     New archetypes needed: **escort**, **collect-and-assemble across the open world**, **survive-waves**.
2. **Missing standalone zones:** `cistern`, `mirage`, `stronghold`, `arena` exist ONLY as `RIFT_KITS` data —
   there are **no builder functions** for them as visitable zones. Either build them or stop referencing
   them as if they're dungeons.
3. **Quest-gate the Rift / Act-1-victory entrance** before any prod promotion.
4. **Final QA pass (all Act 2 zones):** prod-safe (nothing builds without `?dev`), save-safe (no `v`/`questV`
   bump), no console errors, no stuck spots, every quest completable, performance across the bigger map.
5. **Subjective polish (needs the owner's eyes):** per-zone graphics/readability, difficulty/pacing for a
   7-year-old, mountain visual drama, whether the 30%-bigger map feels full enough between landmarks.

## Guardrails (non-negotiable)
- Everything behind `FEAT.act2`. Additive saves only (no `v`/`questV` bump). Never regress the web/desktop
  (prod) path. Commit per increment; don't `git push` unless asked. Verify with `node --check` on the
  extracted `<script id="game">` + the preview before committing.
