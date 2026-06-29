# ACT 2 — Build Progress Log

Append-only-ish log so any iteration can resume. Newest at the bottom of each section.
See `ACT2_GOAL.md` for the definition of done + protocol.

## DONE (committed)
- **Foundation** (`f04006a` and earlier): Act 2 desert — Sun's Rest hub (`buildOasisTown`), open
  Sunscar Dunes (`buildSunscar`), Buried Tomb (`buildTomb`), Sun Temple (`buildSunTemple`, seals puzzle);
  desert mob roster + 5 bosses in `ENEMY_TYPES`; 12 desert uniques (FEAT.act2 push); 2-quest Warden
  questline; ZONE_OFF/ZONE_MIN floors (16→23). All DEV-gated, prod verified clean.
- **Procedural engine P1+P2** (`4b446d4`): mulberry32 seeded RNG; `resolveCollisions()` line-segment
  wall branch (players+enemies, guarded → Act-1 zones inert); `buildRift`/`genRift`/`renderRift`/`kitMats`;
  `rift` zone (procedural:true) + dev button "★ SUNSCAR RIFT (PROC)". VERIFIED in dev: rooms+corridors
  render, walls block (player stopped at a 36u wall, never crossed), regenerates each entry, 23 mobs
  spawn+fight, overworld confirmed inert, no console errors.

## DONE (cont.)
- **P3 — theme kits**: `RIFT_KITS` now has 10 kits (tomb, warren, cistern, crystal, fungal, clockwork,
  pirate, candy, toy, catacombs) as pure data (wall/floor/light/bg/fogD/mobs/boss/props). `buildRift`
  rolls a seeded kit per entry; `renderRift` scatters decorative kit props (no colliders). VERIFIED:
  5 rift entries → 4 distinct kits w/ different palettes + layouts + mob counts; catacombs renders cool
  grey-blue vs warm tomb; no console errors.

## DONE (cont.)
- **P4 (part 1) — set-piece rooms**: `buildRift` now tags rooms by role — boss (farthest from spawn),
  vault (far from both), altar (nearest grid centre) — and stamps them: boss room = raised dais + the
  kit boss (`z.riftBoss`) + dramatic light, no trash; vault = treasure chest + 4 pillars; altar =
  pedestal + emissive gem (`z.altarPos`, the P5 assemble target). Cached `mats.altar` added so teardown
  stays geometry-only (no leak). VERIFIED: candy-kit rift placed GORGEMAW on the dais, altar at
  (7.5,-16.5), chest spawned; Act-1 dungeon still has no wallSegs; no console errors.

## DONE (cont.)
- **P4 (part 2) — locked boss door + key**: boss room is now the chain's leaf (loops excluded from the
  last room → exactly one entrance, no softlock). `buildRift` gates the boss room's doorway tiles
  (ring tiles adjacent to interior floor only — never severs passing corridors) with removable wall
  boxes + `wallSegs` (`z.riftGate`), drops a glowing KEY on a pedestal in the vault (interactable
  kind `riftkey` + POI), and a "🔒 SEALED DOOR" POI. `openVendor` riftkey handler opens it (hides
  boxes + splices segs from `wallSegs`). VERIFIED: gate closes the boss room (typ. 2 segs; up to ~10
  when the access corridor runs along the room edge — still a single sealed approach, no severing);
  taking the key flipped gateOpen + removed all gate segs from collision (64→55); no console errors.
  P4 core set-pieces done (boss/vault/altar/locked-door+key). Lever puzzle folds into P5 charge-nodes;
  weak-wall secret rooms deferred to the QA/polish pass (optional).

## DONE (cont.)
- **P5 — collect-and-assemble (headline quest) + pictogram tracker**: the rift floor's objective is now
  THE SHATTERED SUN-DIAL — 3 sun-shards spread across rooms (interactable `riftshard` + glowing mesh +
  POI), carried to the altar (`riftaltar` at `z.altarPos`); assembling unseals the boss gate
  (`openRiftGate`) + drops a relic. Kid-legible HUD pip tracker `#riftshards` ("🔆 SUN-DIAL ◆◇◇ 1/3"),
  shown/hidden via `updateRiftHUD()` on zone change + pickups. Replaced the placeholder key as the rift's
  gate-opener (legacy `riftkey` handler kept for reuse). State is zone-local + transient (no save fields →
  inherently save-safe). VERIFIED: shard pickup ticked HUD to 1/3; altar assemble opened the gate
  (10→0 segs) + altarDone; no console errors. Other archetypes (charge/captains/waves/drain/free-captives)
  fold into the P6 rift quest-roll + P7 story dungeons.

## DONE (cont.)
- **P6 — the Sunscar Rift loop (endless content)**: `riftTick` opens a glowing DESCEND gate at the boss
  room when `z.riftBoss` dies (interactable `riftdescend` + POI + banner). Descending increments
  `game.riftFloor` and rebuilds (new seed → new kit + layout + omen); `setZone` resets the floor to 1
  only when entering from a non-rift zone (descend keeps climbing). Per-floor scaling sets
  `ZONE_OFF.rift = 1+floor` / `ZONE_MIN.rift = 14+floor*2` (read by enemyStats) + mob density rises with
  depth. Per-floor OMEN roll (Quiet Sands / Restless Halls / Gilded Floor / Blessed Ground / Still Air)
  tweaks mob count, adds shrines, or drops a bonus chest. Floor banner shows "Floor N · kit · omen".
  Fixed: per-floor run-state (`descendReady`/`riftBoss`/`altarDone`) now resets in buildRift so deeper
  floors open their own descend gate. VERIFIED: floors 1→2→3 each reset descendReady + spawn a boss +
  roll an omen; hub re-entry resets to floor 1; descend gate appears on boss death; no console errors.

## NEXT
- **P7 — convert story dungeons + wire the hub**: Tomb/Sun-Temple/Cistern/Stronghold → procedural kits
  (fixed seed for a stable authored feel) + their archetype; Arena/Mirage → set-piece rooms; add Sun's
  Rest doorways/portals into each procedural dungeon + the rift. Then **QA + review checkpoint**
  (screenshots per kit, perf/leak check over 20 rebuilds, prod+web re-verify → ACT2_TESTREPORT.md).

## NOTES / GOTCHAS
- `freeze(root)` only locks matrices (does NOT merge meshes); keep per-build mesh counts sane (walls are
  merged into runs already).
- `buildRift` teardown disposes GEOMETRIES only; kit materials/textures are cached in `__kitMatCache` and
  reused — never dispose them.
- Headless preview throttles rAF when backgrounded; force frames with screenshots when driving puzzles.
- Mobs in a fresh rift can swarm a low-level test char; use the god flag (`game.godMode=true`) when
  inspecting, not for balance judgments.
