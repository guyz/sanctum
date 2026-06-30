# ACT 2 "The Sunscar Reaches" — Test Report & Review Checkpoint

Status: **feature-complete for the current ACT2 goal and objectively verified.** All DEV-gated behind
`FEAT.act2`; prod + web/desktop path unaffected; save additive-only. Subjective pacing/visual polish still
needs owner eyes / a real-device playtest.

## What's built (the act)
- **Sun's Rest** — populated oasis hub (8 NPCs, no overlaps), Warden Khenra questgiver.
- **Sunscar Dunes** — open desert wilderness: continuous desert mob spawns, 4 gates (Buried Tomb,
  Sun Temple, optional standalone zones, arena, the Rift tear, road home), shrines/chests, solid mesa
  blockers, oases.
- **Buried Tomb** — sandstone dungeon + boss KHA'ZRUK.
- **Sun Temple** — light-the-4-seals puzzle dungeon + boss RA-SETH.
- **Cistern Canyon / Mirage Vault / Jackal Stronghold / Howling Arena** — standalone Act 2 zones with
  real builders, portals, colliders, shrines/chests, and seeded encounters.
- **Warden story arc** — six quests: dunes intro, caravan camp investigation/ambush/escort beat, tomb,
  open-world Sun-Dial shard collection and altar assembly, Sun Temple, arena finale.
- **The Sunscar Rift** — the headline: an **endless procedural rooms-and-corridors dungeon**.
  - Seeded generator (rooms + L-corridors, guaranteed connectivity, scrap-and-regen quality gate).
  - **Line-segment wall collision** shared by players + enemies (no AI rewrite).
  - **10 theme kits** (tomb, bandit warren, cistern, crystal caverns, fungal grotto, clockwork vault,
    pirate cove, candy cavern, toy workshop, cute catacombs) — one generator → many worlds.
  - **Set-piece rooms**: boss (dais + boss), treasure vault, the assemble-altar, **locked boss door +
    key** (gated, no-softlock leaf room).
  - **The Shattered Sun-Dial** collect-and-assemble quest: gather 3 shards → carry to the altar →
    auto-fuse → the boss door opens + a relic drops. Kid-legible HUD pip tracker (🔆 ◆◇◇ 1/3).
  - **Endless loop**: clear the floor boss → DESCEND gate → deeper floor (new seed → new kit/layout/omen,
    scaling difficulty). Per-floor **omen** roll (Quiet Sands / Restless Halls / Gilded Floor /
    Blessed Ground / Still Air). Reachable in-world via the dunes rift-tear (+ dev button).
- Desert mob roster + bosses (tinted reskins) and desert uniques — all `FEAT.act2`-gated.

## Verified (objective — automated checks)
- **Syntax**: `node --check` on the extracted game script — clean after every change.
- **Collision**: player walked straight at a 36u wall and stopped at its surface (never crossed);
  Act-1 zones carry no `wallSegs` → the new branch is a no-op there.
- **Generator**: rooms+corridors render; fresh layout every entry (seg counts vary); 25 rebuilds OK.
- **Kits**: ≥5 distinct kits observed across entries (palette/layout/mobs differ); candy/catacombs/tomb/
  pirate confirmed visually distinct.
- **Set-pieces / quest**: shard pickup ticks the HUD (1/3); altar assemble opens the boss gate
  (collision segments removed); locked-door+key flow opens the gate; boss spawns per floor.
- **Rift loop**: floors 1→2→3 each reset run-state + spawn a boss + roll an omen; hub re-entry resets
  to floor 1; descend gate appears on boss death.
- **Performance / leaks**: across 25 rift rebuilds POI DOM nodes stay flat (28), enemies bounded, and
  heap reclaims on idle (185→165 MB) — no runaway leak. Teardown disposes geometries + per-build
  materials/textures while preserving cached kit materials.
- **Readability fix**: figures now stand clearly on the (re-darkened/textured) sand with contact shadows.
- **Safety**: prod build (no `?dev`) builds **none** of the act2/procedural zones; no console errors in
  any zone tested; save state is additive/transient (no `v`/`questV` bump); web/desktop path untouched.
- **2026-06-30 ACT2 pass**:
  - Static script parse clean (`new Function` over all inline scripts).
  - Chrome/Playwright through system Chrome loaded `sanctum-of-ash.html?dev` at desktop 1280×720 and
    mobile 390×844 viewports.
  - All Act 2 zones (`act2town`, `sunscar`, `tomb`, `suntemple`, `cistern`, `mirage`, `stronghold`,
    `arena`) rendered nonblank screenshots with high color variance; no page errors.
  - Six Warden quests present; all new standalone zones have roots, colliders, inbound/outbound portals.
  - Sunscar mesa blockers present for every mesa; sampled mesa heights are elevated; Sun-Dial shard mesh Y
    equals `zoneGroundY('sunscar', x, z)` for all three shards.
  - Gate logic confirmed with dev/god disabled: arena locked before `The Storm-Eater`, arena opens when
    accepted, Rift remains locked during the quest, Rift opens after reward.
  - Shard→altar flow confirmed: three pickups set mask `1→3→7`, hide shard meshes, advance to stage 1;
    altar sets `sunDialAssembled` and marks the quest reward-ready.

## Needs YOUR eyes (subjective — the loop deliberately did not self-certify)
- **Feel / fun on a real device** — a full town→dungeons→rift playthrough with a kid. Pacing, difficulty
  curve, whether the descend loop is compelling.
- **Graphics polish per kit** — do all 10 kits read well *in motion*? (Candy/toy are intentionally
  vivid; flag any that feel off and I'll tune that kit's floor like I did the dunes.)
- **Content length vs Act 1** — the Warden line is now 6 authored quests plus optional zones and the
  endless Rift; decide after playtesting whether it needs more authored beats.

## Optional / deferred (non-blocking)
- Convert the open-disc **Buried Tomb** + **Sun Temple** to fixed-seed procedural kits (parameterize
  `buildRift` with `{kit, seed}` per zone) for full consistency with the rift.
- Weak-wall **secret rooms** and a **lever puzzle** set-piece (P4 extras).
- Gate the rift behind the Warden questline + an Act-1-victory entrance when promoting to prod.

— Built with embedded CC0 assets + procedural geometry; reuse-first, zero new art.
