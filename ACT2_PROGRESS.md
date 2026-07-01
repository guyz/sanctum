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

## DONE (cont.)
- **P7 (part 1) — Rift wired into the world**: added a "Sunscar Rift" tear in the dunes (`buildSunscar`):
  a ring of dark obelisks around a glowing purple portal → `{zone:'rift'}` + POI. The endless procedural
  rift is now reachable in-world (Sun's Rest → dunes → rift tear), not just the dev button; floor resets
  to 1 on entry from the dunes. VERIFIED: tear renders (obelisks + glow), no centre collider so the
  portal is steppable, no console errors.

## DONE (cont.)
- **Readability fix** (`7ca40ab`): the desert sand was washing out figures (read as "sunk"); re-darkened
  + re-textured the dunes sand + tomb-kit floor + toned the over-bright lighting. NOT a height bug —
  all entities verified at y=0; it was contrast.
- **QA pass** (`3c53aaa` + this): fixed rift-rebuild leaks (poiLabels/shrines/chests + per-build
  materials now cleared in teardown; cached kit mats preserved) — POIs flat across 25 rebuilds, heap
  reclaims on idle. Prod re-verified clean (no act2/procedural zones build without ?dev), no console
  errors. Wrote `ACT2_TESTREPORT.md` (full verification + subjective items flagged).

## POST-CHECKPOINT FIXES (user feedback round)
- **Height "bug" re-investigated (definitively NOT in current code)**: at an identical pose the player
  renders the same in sunscar as in the Act-1 dungeon (head+tunic+sword+shadow, standing); scarab+raider
  sit correctly on the darkened sand. The sink the user sees is a **STALE BUILD** (native app bundles an
  HTML snapshot from the last setup-ios.sh; web caches via SW). Action: bumped SW `CACHE` v30→v31; to
  refresh native, re-run `setup-ios.sh dev` + Xcode. (`95071aa`)
- **Town portal fixed** (`95071aa`): removed the Sun's Rest→Act-1-vale portal; the town now only opens to
  the dunes (Act 2 self-contained).
- **Content**: Warden questline extended to 4 quests (dunes→tomb→Sun Temple→Rift) — verified the Sun
  Temple seal-puzzle quest credits 1→4 + advances to the RA-SETH boss stage. (`332dbeb`)
- **QA sweep**: all 5 act2 zones build+render (wallSegs only on rift=85), no console errors; prod clean.

## POST-CHECKPOINT FIXES (user feedback round 2 — town + mob variety)
- **Town rework** (`buildOasisTown`): the user said Sun's Rest was compressed, mis-oriented, and
  "not desert-like." Swapped the medieval green-roof GLB house kit for the procedural flat-roof ADOBE
  `building()` (parapets/domes/awnings/sandstone courses), every door now faces the oasis plaza;
  spread the house ring r15-26 → r19-42 with 4.5u gaps (14 houses); added packed-sand STREETS fanning
  from the plaza (main road aimed at the dunes gate); moved boundary fences out to r46-50 (outside the
  houses). VERIFIED in preview: adobe houses spaced along streets, player reads clearly on sand, desert
  flora (cacti/palms) intact, no console errors.
- **Mob variety**: the user said too many Act-1 reskins remained. Added 9 DISTINCT-SILHOUETTE desert
  creatures from embedded CC0 monster models (none humanoid): Bristle Cactus (gaunt_cactus), Dune Stalker
  (raptor), Sand Hornet (wasp), Quicksand Maw (mawgooey), Oasis Sporeling (gaunt_mush), Sun Ifrit (demon),
  Dune Behemoth (gaunt_yeti), Bone Tyrant (trex), Dune Wyvern (dragon2). Wired into the player-facing
  zones — dunes mix+opening (lizard/hornet/cactus + roaming wyvern elite), tomb (Quicksand Maw + Bone
  Tyrant elite), Sun Temple (Sun Ifrits), Cistern (Sporelings), and 6 rift kits. VERIFIED: all 9 build
  with models + spawn from the director, every anim clip confirmed present per model, dragon/wyvern
  silhouette renders distinct, zero console errors. (Note: dunewyvern reads quite red — acceptable as a
  fire-wyvern; could tint sandier in a later polish pass if desired.)

## GOAL RELAUNCH (2026-06-30): bigger world + content (user-set goal)
- **Mountain bug — verified solved across all Act 2 zones**: sunscar is a terrain heightfield (ride it,
  blocked at the rim), no leftover mesh mountains; act2town has no horizon mesas; tomb/suntemple are
  flat-floor + wall colliders. (Task #21)
- **World expanded ~30% bigger than Act 1**: `zones.sunscar.r` 96→215 (Act 1 = 165). Terrain/rim/clamp/
  foliage-spread auto-scale from R; spawns are player-relative + minimap is player-local (auto). Gates
  spread to compass edges (S home, N tomb, W temple, E rift) as rim-notch passes, each with matching
  flatten-zone + entry + dungeon-exit. Density ~3×; SGRID 128→200, ground mesh 232 segs; zone-aware
  camera far (sunscar 360) + a bit more haze. (Task #22, committed)
- **Landmarks + named encounters**: Sunken Colossus, Raider Camp (+captain), Bone Field (+Bone Tyrant),
  Ruined Watchtower — each a POI beacon on the heightfield; south-gate welcome wave; relics scaled
  (6 shrines/12 chests). (Task #23, committed)
- **NEXT — Task #24**: a multi-stage Act 2 storyline tying the landmarks/dungeons together with varied
  quest archetypes (the Warden line is currently only 4). Plan proposed to the user for a steer first.

## GOAL RELAUNCH COMPLETED (2026-06-30): Act 2 architecture + story pass
- **Baseline preserved**: committed the pre-existing dirty `.codex/config.toml` first, then committed the
  terrain/elevation architecture fix separately.
- **Terrain/elevation architecture fixed** (`f2c032c`): Act 2 no longer has its own one-off terrain logic.
  `zoneGroundY()` / `groundY()` are zone-aware; Sunscar static children are settled with the same shared
  pass as Act 1; portals, enemies, pickups, shadows, click/held movement, minimap boundary, projectiles,
  and spawn clamps all use zone-aware terrain/radius. Sunscar now has `walkR` inside its visible rim.
- **Mountains are real blockers**: all eight Sunscar mesas use one shared `SUNSCAR_MESAS` table for separate
  scenery meshes plus circular colliders, matching Act 1's open-world pattern. Mesas are not part of the
  walkable heightfield.
- **Warden storyline expanded to 6 quests**: `Sand in the Wells` → `The Caravan's Bones` →
  `The Buried King` → `Shards of the Sun-Dial` → `The Sealed Light` → `The Storm-Eater`.
  Added stage-aware visit/ambush progression and fixed quest guide routing so entrance markers and
  in-zone objectives do not collapse into the old Act-1 "HUNT HERE" assumption.
- **Sun-Dial open-world collection built**: three Sunscar shard interactables now settle onto the terrain,
  hide after pickup, save via additive fields (`act2ShardMask`, `sunDialAssembled`), and advance to the
  central altar stage. The altar completes the quest objective.
- **Standalone Act 2 zones built**: `cistern`, `mirage`, `stronghold`, and `arena` now have real builders,
  portals, POIs, colliders, shrine/chest placement, and seeded encounters. They are no longer referenced
  only as Rift kits.
- **Rift progression gated**: arena unlocks when `The Storm-Eater` is accepted; Rift unlocks only after
  that quest is rewarded (dev/god bypass remains intentional for tooling).
- **Verification**: `node` script parse clean; Chrome/Playwright via system Chrome loaded `?dev` in
  desktop and mobile viewports, rendered all Act 2 zones with nonblank screenshot stats, reported no page
  errors, confirmed 6 Warden quests, confirmed all standalone zones/portals/colliders exist, confirmed
  mesa blockers, confirmed shard mesh Y equals Sunscar terrain Y, confirmed Rift gate logic, and confirmed
  shard→altar quest progression.

## BUGFIX FOLLOW-UP (2026-06-30): Sunscar mesa walkability
- **Root cause**: the first elevation fix made Sunscar terrain zone-aware, but still put mesa mountains into
  the same heightfield the player walks on. Act 1 does not do that; its mountains/rocks are separate scenery
  with colliders or live outside the playable clamp.
- **Fix**: `buildSunscarTerrain()` now produces walkable dunes only. `SUNSCAR_MESAS` feed `addSunscarMesa()`
  meshes and matching circular colliders; the visual rim begins beyond `walkR`.
- **Verification**: static script parse clean; Chrome/Playwright sampled every Sunscar mesa center at low
  dune elevation, pushed test points out to each mesa collider radius, and confirmed the rim stays low at
  the clamp while rising outside the playable area.

## BUGFIX FOLLOW-UP (2026-06-30): Sunscar terrain-surface contract
- **Root cause**: the mesa proof was too narrow. Sunscar had a displaced heightfield, but the engine did not
  treat that mesh as the zone's pickable terrain surface: cursor targeting fell back to the flat plane, the
  ground mesh was not explicitly protected from prop-settling, and click targets square-clamped toward
  invalid rim/corner space.
- **Fix**: Sunscar keeps its `kind: 'dungeon'` semantics, but stores its displaced terrain as
  `zones.sunscar.gmesh`, marks that mesh `noTerrain`, and click/held-click/meteor targets use
  `clampToWalkDisc()` for radial clamping. Circle-collider resolution now takes a short second pass so
  overlapping mesa/rock blockers do not leave residual penetration.
- **Verification**: static script parse and `git diff --check` clean; Chrome/Playwright confirmed Sunscar
  `kind === 'dungeon'`, `gmesh.userData.noTerrain`, radial clamp samples, mesa blockers, and 16 forced
  rim probes resolving to `d=196` with low `groundY` while the visual rim still rises outside the walk disc.

## BUGFIX FOLLOW-UP (2026-07-01): Sun's Rest surrounding terrain
- **Root cause**: the persistent report was in `act2town`, not `sunscar`. Sun's Rest still used a flat
  plane plus decorative half-sphere dune meshes, and the first heightfield fix kept the town as a tiny
  `walkR=54` disc, so the visual rim became a steep sand wall beside the player instead of distant outskirts.
- **Fix**: added `buildAct2TownTerrain()` / `sampleAct2Town()` and routed `zoneGroundY('act2town', x, z)`
  through that heightfield. `buildOasisTown()` now builds a displaced desert terrain mesh from the grid,
  registers it as `zones.act2town.gmesh`, marks it `noTerrain`, removes the old half-dome dune ridge meshes,
  settles town props onto the heightfield, and expands Sun's Rest to Act-1-scale outskirts (`r=165`,
  `walkR=150`) with the Act-1 far-rim profile.
- **Verification**: static script parse clean; Chrome/Playwright loaded `?dev`, confirmed `act2town` has a
  terrain `gmesh` with 50,625 vertices and `noTerrain`, plaza and dunes gate samples stay at `0`, the old
  problem radius off-road is only `0.306`, mid-outskirts are rolling at `4.289`, distant rim samples rise
  around `15`, forced player position `(180,0)` resolves to `d=150`, `y=0`, and there are no console warnings.
  Screenshot `/tmp/sanctum-act2town-outskirts.png` confirmed open sand at the old wall location.

## STATUS: feature-complete; autonomous loop PAUSED
The objective acceptance criteria are met + verified (engine/collision/kits/set-pieces/quests/rift/
leak/prod-safety). Remaining items are SUBJECTIVE (feel/fun/graphics — need the user) or OPTIONAL
(convert open-disc Tomb/Sun-Temple to fixed-seed procedural kits; secret rooms/lever; quest-gate the
rift for prod promotion). The cron loop was deleted at this checkpoint. To resume: tell me "continue"
(I'll re-create the loop) or point me at a specific fix.

## NOTES / GOTCHAS
- `freeze(root)` only locks matrices (does NOT merge meshes); keep per-build mesh counts sane (walls are
  merged into runs already).
- `buildRift` teardown disposes GEOMETRIES only; kit materials/textures are cached in `__kitMatCache` and
  reused — never dispose them.
- Headless preview throttles rAF when backgrounded; force frames with screenshots when driving puzzles.
- Mobs in a fresh rift can swarm a low-level test char; use the god flag (`game.godMode=true`) when
  inspecting, not for balance judgments.
