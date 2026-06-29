# ACT 2 "The Sunscar Reaches" — Test Report & Review Checkpoint

Status: **feature-complete and objectively verified.** All DEV-gated behind `FEAT.act2`;
prod + web/desktop path unaffected; save additive-only. The autonomous build loop is paused here
(it can't self-certify the subjective bars below — those need your eyes / a real-device playtest).

## What's built (the act)
- **Sun's Rest** — populated oasis hub (8 NPCs, no overlaps), Warden Khenra questgiver.
- **Sunscar Dunes** — open desert wilderness: continuous desert mob spawns, 4 gates (Buried Tomb,
  Sun Temple, the Rift tear, road home), shrines/chests, rock mesas, oases.
- **Buried Tomb** — sandstone dungeon + boss KHA'ZRUK.
- **Sun Temple** — light-the-4-seals puzzle dungeon + boss RA-SETH.
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

## Needs YOUR eyes (subjective — the loop deliberately did not self-certify)
- **Feel / fun on a real device** — a full town→dungeons→rift playthrough with a kid. Pacing, difficulty
  curve, whether the descend loop is compelling.
- **Graphics polish per kit** — do all 10 kits read well *in motion*? (Candy/toy are intentionally
  vivid; flag any that feel off and I'll tune that kit's floor like I did the dunes.)
- **Content length vs Act 1** — the Rift is endless, but the hand-authored *story-quest* count is lower
  than Act 1's 15. If you want more authored questline, that's a follow-up.

## Optional / deferred (non-blocking)
- Convert the open-disc **Buried Tomb** + **Sun Temple** to fixed-seed procedural kits (parameterize
  `buildRift` with `{kit, seed}` per zone) for full consistency with the rift.
- Weak-wall **secret rooms** and a **lever puzzle** set-piece (P4 extras).
- Gate the rift behind the Warden questline + an Act-1-victory entrance when promoting to prod.

— Built with embedded CC0 assets + procedural geometry; reuse-first, zero new art.
