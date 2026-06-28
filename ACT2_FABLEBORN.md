# Fableborn — Act II: The Sunscar Reaches (build plan)

> **Goal:** a full, Diablo-2-style second act — a *desert/oasis* region contrasting Act 1's green Vale.
> New town, NPCs, mobs, items, dungeons, and a unique questline. **DEV-only** (`FEAT.act2 = DEV_BUILD`)
> until it's fleshed out, so it never touches the live game. Built on `main` behind the dev channel —
> this is exactly what the prod/dev split was for.

## Theme & story
Act 1 cleansed the **Vale of Embers** (green). Act 2 heads **south into the Sunscar Reaches** — a sea of
dunes around the dying oasis town of **Sun's Rest**. A buried tyrant / sun-curse is swallowing the oasis;
the hero must descend into a buried tomb and break the curse at the heart of the sands.

Look & feel: bright sun-bleached sand, wind ripples, oasis water + palms, sandstone/adobe buildings,
mesas and canyons. Warmer, drier, higher-contrast than the Vale.

## What's built so far
- ✅ **Phase 0 — `Sun's Rest` oasis hub** (`buildOasisTown()`, zone `act2town`): procedural sand ground
  with wind ripples, an oasis pool + sandy rim, palms, sandstone buildings (door + flat roof), desert
  rocks, daylight grade, and a DEV portal back to the Vale. Reachable in dev via the pause-screen
  **★ DESERT (ACT II)** travel button. Verified rendering in dev; **absent in prod** (not built, button hidden).

## How it's gated / accessed
- `FEAT.act2 = DEV_BUILD` (in the `FEAT` block). `buildOasisTown()` is only called at boot when `FEAT.act2`.
- Zone `act2town` is *registered* always (inert data; `setZone`'s `if (zz.root)` guard skips it in prod).
- Dev entry: pause → **★ DESERT (ACT II)**. (`devtravel` is hidden in prod.) Later: a real in-world
  southern desert portal from the Vale, gated behind Act 1 victory, when promoted to prod.

## Design (to build)
**Town — Sun's Rest:** new NPCs reusing the vendor framework (elder/baker/smith/apothecary/innmaster
patterns): an **oasis elder / watchkeeper** (Act 2 questgiver), a **water-trader/relic merchant**, a
**desert smith**. POIs + beacons like the Vale town.

**Mobs (desert roster):** mostly reskins/tints of embedded models + a few sourced:
- Sand Raider (bandit, sandy), Dust Jackal (wolf, tan), Sand Wraith (wraith, ochre, ranged),
  Pit Viper (already desert-appropriate), Tomb Mummy (skeleton, bandaged tint — for the tomb),
  Scarab/Scorpion (SOURCE a model), brute = Sand Brute (tinted).
- Boss: a **Giant Scorpion ("Kha'zruk")** or **Mummy Lord / Sand Colossus** (source or tint a boss model).
- All tuned to the bounded-TTK model; add `ZONE_OFF`/`ZONE_MIN` entries for desert zones (run above Act 1).

**Zones:** `act2town` (hub ✅) · **The Sunscar Dunes** (open desert wilderness w/ mobs) · **The Buried
Tomb** (sandstone dungeon — mummies/scarabs + boss) · optional **Oasis Cistern** cave / canyon dungeon.

**Questline (unique, ~5 stages):** Sand in the Wells → The Watcher's Warning (find the buried obelisk)
→ Into the Tomb (light the seals) → The Scarab King / Mummy Lord (tomb boss) → Break the Sun-Curse
(final boss in the deep Sunscar). Uses the existing multi-stage quest + zone-unlock systems; appended to
`QUESTS` after Act 1, gated to appear post-Act-1-victory.

**Items:** desert uniques (e.g. Sunscar Khopesh, Mirage Veil, Scarab Heart) via the existing
`makeItem`/`makeUnique`/loot tables.

## Assets (CC0 — from the credits link)
- **Reuse (already embedded):** skeleton→mummy, bandit/rogue→raider, wolf→jackal, wraith→sand wraith,
  snake (Pit Viper), modular dungeon kit→sandstone tomb (tint), nature kit.
- **Source & embed (CC0):** palm trees (Kenney *Pirate Kit* / poly.pizza), sandstone/adobe buildings
  (Quaternius *Medieval Village* tinted, or Kenney *Fantasy Town*), **scorpion/scarab** (poly.pizza/
  Quaternius), cliffs/mesas (Kenney *Nature Kit*), optional desert boss.
- **Pipeline:** download GLB → gltf-transform (`mergeDocuments`+`dedup`+`unpartition`, drop anims) →
  base64 into `window.MODELS` (same as the existing kits). NOTE: embedded assets ship in the prod file
  too (inert) → watch total size; if it grows large, serve Act 2 assets via the Capgo OTA bundle later.

## Roadmap
- ✅ **0** Foundation: Sun's Rest oasis hub, dev-gated, rendering.
- **1** Assets: source + embed desert GLBs (palms, sandstone, scorpion, mummy tint).
- **2** The Sunscar Dunes wilderness + balanced desert mob roster.
- **3** Town NPCs + vendors + the Act 2 questline.
- **4** The Buried Tomb dungeon + boss.
- **5** Items/uniques + a 2nd dungeon + polish.
- **6** Promote to prod: in-world desert entrance gated behind Act 1 victory, balance pass, ship via OTA.

> The old `act2` branch ("Trials of Ash" — a portal hub of reused dungeons) is **superseded** by this
> desert act on `main`. See [[act2-parked-branch]] / [[publishing-architecture]] in memory.
