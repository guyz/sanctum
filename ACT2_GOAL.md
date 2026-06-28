# ACT 2 — Definition of Done & Autonomous Build Protocol

**Goal:** Complete Act 2 "The Sunscar Reaches" to a bar **≥ Act 1** — a procedural-dungeon-driven
desert act, fully playable from the Sun's Rest hub, **DEV-gated, save-safe, prod + web untouched**.
This file + `ACT2_PROGRESS.md` + the committed code + `git log` are the single source of truth so any
iteration (even a cold one with no chat context) can resume correctly. Plan basis: `ACT2_FABLEBORN.md`
and the procedural-redesign spec (rooms-and-corridors generator + theme kits + set-pieces + new quests).

## Objective acceptance criteria (I verify these myself)
- [x] **Procedural engine**: rooms+corridors generator, line-segment wall collision (players+enemies),
  seeded (mulberry32), rebuild-per-entry (`buildRift`). DONE — committed.
- [ ] **≥8 theme kits** (P3): 2 desert (Sunken Tomb, Bandit Warren) + classic (Cistern, Crystal
  Caverns, Fungal Grotto, Clockwork Vault) + playful (Pirate Cove / Candy Cavern / Toy Workshop) +
  spooky-but-cute (Cute Catacombs). Each visually distinct: palette, wall/floor mat, props, mob table, light/fog.
- [ ] **Set-piece rooms** (P4): boss, treasure/vault, locked-door+key, lever puzzle, collect-assemble
  altar, secret room — tagged by role after generation and stamped as string-grid prefabs.
- [ ] **Quest archetypes** (P5): collect-and-assemble (Shattered Sun-Dial: 3 shards → altar auto-fuse →
  visible world change) FIRST, + charge-nodes, build/repair, beat-the-captains, survive-waves, drain,
  free-captives. Pictogram HUD trackers. **Additive save booleans only.**
- [ ] **The Sunscar Rift** (P6): one hub portal; rolling kit × layout × quest × modifier roll (≤3
  boons/banes) + shrine anchors; clear boss room → descend (new seed, scaling); expose seed.
- [ ] **Story dungeons converted** (P7): Tomb/Sun-Temple/Cistern/Stronghold → procedural kits (fixed
  seed for stable authored feel) + their quests; Arena/Mirage → set-piece rooms; Sun's Rest doorways wired.
- [ ] **Content ≥ Act 1**: ≥6 distinct dungeon experiences, ≥10 quests (several multi-stage), a boss per
  major dungeon, endless Rift. Target playtime ≥ ~1.5–2 h.
- [ ] **No bugs**: no console errors; no crashes; no stuck spots in corridors/doorways; bosses spawn;
  every quest completable end-to-end; loot/XP/scaling sane (ZONE_OFF/ZONE_MIN entries for all new zones).
- [ ] **Performance**: heap stable across ≥20 rift rebuilds (no leak); acceptable FPS; reasonable draw calls.
- [ ] **Safety**: save additive-only (NO `v`/`questV` bump); prod build = none of this builds or is
  reachable; web/desktop path byte-for-byte unchanged. Re-verified at the QA pass.

## Subjective bars (build to these, then FLAG for the user with screenshots — do NOT self-certify)
- Per-kit graphics/readability, lighting, minimap clarity.
- Kid UX (age 7): one tracked objective at a time, waypoint/breadcrumb, big pictograms, **no hard-fails**,
  telegraphed bosses, forgiving difficulty.
- Overall fun/variety.

## Build order (each phase = one or more verified, committed increments)
P3 kits → P4 set-pieces → P5 quests → P6 Rift → P7 conversions → **QA/polish + review checkpoint**.

## Autonomous iteration protocol (run this each loop firing)
1. Read this file + `ACT2_PROGRESS.md`; run `git log --oneline -15`. Pick the next unfinished item.
2. Implement the next coherent chunk.
3. **Verify**: extract `<script id="game">` and `node --check` it; CSS brace balance if HTML/CSS touched;
   load the preview (`http://localhost:8841/sanctum-of-ash.html?cb=<ts>&dev`, server name `sanctum`),
   drive via the `window.__sanctum` hook (setZone, spawnEnemy, player.group.position, renderOnce),
   screenshot the affected zones, check `preview_console_logs` level=error returns none, sanity-check an
   Act-1 zone is unaffected. Watch for stuck spots / leaks.
4. **Commit locally** (never `git push` unless the user asks) with a clear message ending in the
   Co-Authored-By line. Update `ACT2_PROGRESS.md` (done / verification result / next step).
5. If ALL objective criteria are met → write `ACT2_TESTREPORT.md` (what was verified + remaining
   subjective items), capture a screenshot per kit/dungeon, **delete the autonomous cron job**, and
   notify the user with the review checkpoint.
6. If blocked on a subjective or risky/destructive decision → STOP and ask the user.

## Guardrails (non-negotiable)
- Everything behind `FEAT.act2`. Save additive-only (see `save-data-safety` memory). Never edit
  prod-shared UI or the web/desktop entry path (`web-interface-untouched` memory). Commit per increment;
  **do not push**. Stay on `main` (the established workflow for this dev-gated work).

## Key engine anchors (keep current)
- Collision: `resolveCollisions()` has a guarded `wallSegs` segment branch; `wallSegs` aliased in
  `setZone` (`z.wallSegs || EMPTY_SEGS`); open-disc zones carry none → no-op.
- Procedural: `RIFT`, `mulberry32`, `nextRiftSeed`, `RIFT_KITS`, `kitMats`, `genRift`, `renderRift`,
  `buildRift` — defined just before `buildVolcano()`. `buildRift` runs from `setZone` when `z.procedural`.
  `ACT2_PUZZLE` set makes the director leave population to the builder/tick.
- Content tables: `zones` registry (~13071), `ENEMY_TYPES`, `UNIQUE_ITEMS` (FEAT.act2 push), `QUESTS`
  (FEAT.act2 push) + `ZONE_UNLOCK`, `openVendor` warden case, `GIVER_NAME/LOC.warden`.
- Per-frame zone hooks: `act2Tick(pos,dt)` beside `castleTick`; `act2ApplyState(key)` beside
  `castleApplyState` in `setZone`.
- Verify harness: extract game script → `node --check`; preview server `sanctum` :8841; `?dev` =
  dev channel; `window.__sanctum` debug hook (game/player/zones/setZone/spawnEnemy/renderOnce/...).
