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

## NEXT
- **P3 — theme kits**: expand `RIFT_KITS` to ≥8 distinct kits (data); wire kit selection per dungeon/rift
  floor; verify each renders as a visibly different world. (One `tomb` kit exists as the template.)
- then P4 set-pieces → P5 quests → P6 rift descent+modifiers → P7 convert story dungeons → QA + checkpoint.

## NOTES / GOTCHAS
- `freeze(root)` only locks matrices (does NOT merge meshes); keep per-build mesh counts sane (walls are
  merged into runs already).
- `buildRift` teardown disposes GEOMETRIES only; kit materials/textures are cached in `__kitMatCache` and
  reused — never dispose them.
- Headless preview throttles rAF when backgrounded; force frames with screenshots when driving puzzles.
- Mobs in a fresh rift can swarm a low-level test char; use the god flag (`game.godMode=true`) when
  inspecting, not for balance judgments.
