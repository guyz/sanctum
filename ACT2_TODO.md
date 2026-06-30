# Act 2 "The Sunscar Reaches" — State & TODO (handoff)

Single source of truth for what Act 2 **has**, what's **not built**, and the mountain/elevation bug history.
Everything Act-2 is in the one file `sanctum-of-ash.html` (~31MB; game JS is in
`<script id="game">`; huge base64 lines — always grep length-filtered: `awk 'length($0)<300 && /X/{print NR": "$0}'`).

## 2026-06-30 current status
- **Elevation / mountains are fixed in code.** Act 2 now shares the Act-1 open-world terrain architecture:
  `zoneGroundY()` / `groundY()` are zone-aware, static Sunscar props settle with `settleTerrainChildren()`,
  pickups/portals/enemies use zone-aware terrain height, Sunscar has a smaller `walkR` than its visual rim,
  Sunscar is registered as an `overworld`-kind zone with a real `gmesh` for cursor picking, click targets
  clamp to the circular walk disc, and all eight landmark mesas have matching hard blockers.
- **The Warden line is now the intended 6-quest arc**:
  `Sand in the Wells` → `The Caravan's Bones` → `The Buried King` →
  `Shards of the Sun-Dial` → `The Sealed Light` → `The Storm-Eater`.
- **Standalone Act 2 zones now exist:** `cistern`, `mirage`, `stronghold`, and `arena` have builders,
  portals, colliders, shrines/chests, and encounter seeds. They are no longer fake kit-only references.
- **The Rift is story-gated.** The arena opens when `The Storm-Eater` is accepted; the Rift opens only
  after that quest is rewarded (dev/god modes still intentionally bypass locks).
- Verified in Chrome via `http://127.0.0.1:8877/sanctum-of-ash.html?dev`: syntax clean, desktop/mobile
  screenshots nonblank for all Act 2 zones, no page errors, shard elevation matches Sunscar terrain,
  mesa blockers present, shard→altar quest flow completes, and gate logic matches the above.

## How it's gated / how to run
- **All Act 2 is DEV-only**, behind `FEAT.act2 = DEV_BUILD`. `CHANNEL='dev'` only on localhost with `?dev`
  (or native `setup-ios.sh dev`). Public/prod ships `window.__CHANNEL='prod'` → none of this builds. Prod is clean.
- Run/test: `localhost:8841/sanctum-of-ash.html?dev` → CONTINUE/NEW GAME → the desert is Act 2.
- Build stamp prints to console + (touch builds) the title footer: `window.__BUILD`. **Confirm the stamp
  before judging a bug — stale browser/native bundles have repeatedly masked fixes.**
- Save-safe rule: additive fields only, never bump `v` (2) or `questV` (7). Web/desktop path untouched.

---

## ✅ WHAT ACT 2 CURRENTLY HAS (built + committed on `main`)

**Zones** (registry ~line 13160; builders are `buildOasisTown`, `buildSunscar`, `buildTomb`, `buildSunTemple`,
`buildCistern`, `buildMirage`, `buildStronghold`, `buildArena`):
- **Sun's Rest** (`act2town`) — oasis hub; adobe (flat-roof) houses, spaced with streets, NPCs, the
  questgiver **Warden Khenra**, market/well/bonfire. (Reworked from the old cramped medieval look.)
- **The Sunscar Dunes** (`sunscar`) — the open world. **Now R=215 (~30% bigger than Act 1's `OVERWORLD_R`=165).**
  Real terrain heightfield, gates spread to compass edges (S=home, N=Tomb, W=Sun Temple, E=Rift), 4 oases,
  8 landmark mesas baked into the terrain, ~3× foliage density, 6 shrines / 12 chests.
- **The Buried Tomb** (`tomb`) — sandstone dungeon, boss **KHA'ZRUK**.
- **The Sun Temple** (`suntemple`) — light-the-4-seals puzzle, boss **RA-SETH**.
- **Cistern Canyon** (`cistern`), **Mirage Vault** (`mirage`), **Jackal Stronghold** (`stronghold`),
  **Howling Arena** (`arena`) — standalone Act 2 combat/exploration zones with real builders.
- **The Sunscar Rift** (`rift`) — endless procedural rooms-and-corridors; 10 theme kits; set-pieces
  (boss/vault/altar/locked-door+key); collect-3-shards "Sun-Dial" quest; descend loop with per-floor omen.

**Landmarks (POI beacons in `sunscar`)**: Sunken Colossus (-50,-95), Raider Camp (+captain) (125,-125),
Bone Field (+Bone Tyrant) (-135,120), Ruined Watchtower (95,115). Named elite encounters spawn at the
camp and bone field on entry.

**Mobs** (`ENEMY_TYPES`): Act-1 tinted reskins PLUS 9 distinct-silhouette desert creatures —
`sandcactus, dunelizard, sandhornet, sunmaw, sporeling, sunifrit, dunebehemoth, bonetyrant, dunewyvern`
(+ bosses tombboss/cisternboss/templeboss/mirageboss/strongboss/arenaboss). Wired into dunes/tomb/temple
mixes + 6 rift kits.

**Quests** (`if (FEAT.act2) QUESTS.push(...)`, ~line 18615) — **6** (the Warden line):
`Sand in the Wells` → `The Caravan's Bones` → `The Buried King` → `Shards of the Sun-Dial` →
`The Sealed Light` → `The Storm-Eater`.

**Other (global, but relevant)**: a Lv-20 **Masteries** tier (Spirit Wolf / Sun Totem / Aegis Ward),
DEV-gated `FEAT.masteries`. Town-portal recall + CONTINUE now return to the correct act (act2town).
Cloud sync / Sign in with Apple is wired for the native build (separate from Act 2).

---

## ✅ RESOLVED BUG #1 — "walking into / through mountains" in Act 2

The earlier version made Sunscar look like terrain but did not architect it like Act 1. The fixed version
shares zone-aware terrain sampling and terrain-settling across zones, registers Sunscar as open-world
terrain with a real `gmesh`, keeps the visual rim beyond the playable radius (`walkR`), clamps click targets
to the walk disc, and makes mid-map mesas separate collidable scenery instead of walkable ground.

**What was tried (all on `sunscar`):**
1. Per-object cylinder colliders on mesh "mesas", collider-radius tweaks, player Y-offsets, sand color/contrast.
2. Final approach (current code): Act 2 now follows Act 1's open-world split. `buildSunscarTerrain()`
   (~line 14734) builds only the **walkable dune heightfield**; `sampleSunscar(x,z)` (~14759) samples it;
   `groundY(x,z)` (~14711) returns it for `sunscar`; the displaced ground mesh is in `buildSunscar`
   (~15422). The perimeter rim starts outside `walkR`, and the landmark mesas are generated by
   `addSunscarMesa()` from `SUNSCAR_MESAS` as separate meshes plus circular colliders in `resolveCollisions()`.
   `zones.sunscar.kind === 'overworld'`, `zones.sunscar.gmesh` points at the displaced terrain mesh, and
   `clampToWalkDisc()` keeps click/held-click targets inside the same circular boundary that
   `resolveCollisions()` enforces. Players/enemies ride `groundY` for walkable ground only, then
   blockers/clamps decide what is impassable.

**Still check on a real device:** stale browser/native bundles have repeatedly masked fixes. Confirm
`window.__BUILD` or the native bundle date before judging any recurring report.

Anchors: `groundY` ~14711 · `buildSunscarTerrain` ~14734 · `sampleSunscar` ~14759 · `SUNSCAR_MESAS` /
`addSunscarMesa` ~14646/~14875 · ground mesh in `buildSunscar` ~15478 · `WORLD_R` set in `setZone`
(grep `WORLD_R = z.r`) · clamp in `resolveCollisions` (grep `dc > WORLD_R`) · `OVERWORLD_R`/`DUNGEON_R`
~12776.

---

## ✅ BUILT FROM THE OLD TODO

1. Multi-stage Warden story arc.
2. Standalone `cistern`, `mirage`, `stronghold`, `arena` zones.
3. Quest-gated arena/Rift progression.

## 🟡 REMAINING TODO / POLISH

1. **Act-1-victory entrance / production promotion path** before any prod release.
2. **Final real-device QA pass (all Act 2 zones):** prod-safe (nothing builds without `?dev`), save-safe
   (no `v`/`questV` bump), no console errors, no stuck spots, every quest completable, performance across
   the bigger map.
3. **Subjective polish (needs the owner's eyes):** per-zone graphics/readability, difficulty/pacing for a
   7-year-old, mountain visual drama, whether the 30%-bigger map feels full enough between landmarks.

## Guardrails (non-negotiable)
- Everything behind `FEAT.act2`. Additive saves only (no `v`/`questV` bump). Never regress the web/desktop
  (prod) path. Commit per increment; don't `git push` unless asked. Verify with `node --check` on the
  extracted `<script id="game">` + the preview before committing.
