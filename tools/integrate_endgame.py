#!/usr/bin/env python3
"""Integrate the Ashen Rift + Champions' Gauntlet endgame designs into sanctum-of-ash.html.

Applies the two revised, anchor-verified designs (rift_final.json / gauntlet_final.json) with
the shared/overlapping edits hand-merged into single unified edits. Every op asserts anchor
uniqueness (Patcher), so a bad anchor fails loudly instead of corrupting the 27MB file.
"""
import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
from apply_patch import Patcher

ROOT = os.path.dirname(os.path.dirname(__file__))
p = Patcher(os.path.join(ROOT, "sanctum-of-ash.html"))
rift = json.load(open("/tmp/endgame/rift_final.json"))
gaunt = json.load(open("/tmp/endgame/gauntlet_final.json"))


def apply_edit(e):
    if e["mode"] == "after":
        p.after(e["anchor"], e["snippet"])
    elif e["mode"] == "before":
        p.before(e["anchor"], e["snippet"])
    else:
        p.replace(e["anchor"], e["snippet"])


# ============================ SECTION 1: rift newCode ============================
nc = {b["id"]: b for b in rift["newCode"]}
p.after(nc["rift-state-and-defs"]["insertAfterAnchor"], nc["rift-state-and-defs"]["code"])
p.after(nc["rift-theme-and-pickers"]["insertAfterAnchor"], nc["rift-theme-and-pickers"]["code"])
# blocks 3-7 are chained (each anchors on the prior block's tail) AND block 6's anchor
# `player.potions++;}` already exists once in the live file -> concatenate and insert once.
concat = (nc["rift-run-machine"]["code"] + nc["rift-per-frame-and-clear"]["code"] +
          nc["rift-rewards"]["code"] + nc["rift-ui-panels"]["code"] + nc["rift-town-obelisk"]["code"])
p.after(nc["rift-run-machine"]["insertAfterAnchor"], concat)

# ============================ SECTION 2: gauntlet newCode ============================
gnc = {b["id"]: b for b in gaunt["newCode"]}
# The JSON anchor was only the FIRST line of the tigerboss entry -> would insert the new entry INSIDE
# tigerboss's object literal (valid syntax, but ENEMY_TYPES.gauntlet_ashlord would never exist). Anchor on
# the FULL tigerboss line (it is the last ENEMY_TYPES entry) so the capstone lands as a sibling key.
TIGER_FULL = ("  tigerboss:  { name: 'GORGEMAW, THE HOLLOW HUNGER', hp: 820, dmg: 32, spd: 4.2, xp: 470, "
              "gold: [60, 100], scale: 1.9, body: 0xb8d8ee, accent: 0x4a6a88, eye: 0xaaeeff, range: 3.6, "
              "atkCd: 1.8, brute: true, boss: true, model: 'mawgooey', tint: 0xcfe8ff, anims: { idle: "
              "'IdleFinal', walk: 'Walk', run: 'Walk', atk: 'Attack', death: 'Death' }, runTs: 1.5 },")
p.after(TIGER_FULL, "\n" + gnc["gauntlet_enemy_type"]["code"])
p.after(gnc["gauntlet_gate_props_array"]["insertAfterAnchor"], gnc["gauntlet_gate_props_array"]["code"])
p.after(gnc["gauntlet_gate_pulse_in_atmosphere"]["insertAfterAnchor"], gnc["gauntlet_gate_pulse_in_atmosphere"]["code"])

core = gnc["gauntlet_core"]["code"]
# (a) give the HASTE TOTEM an hp pool
core = core.replace(
    "const t = { kind: 'totem', group: grp, mesh: orb, hit, dead: false };",
    "const t = { kind: 'totem', group: grp, mesh: orb, hit, dead: false, hp: 60 * gauntlet.power };")
assert "hp: 60 * gauntlet.power" in core, "totem hp injection failed"
# (b) remove the dead-code stub
core = core.replace("function gauntletStart_noop() {}\n", "")
# (c) make the totem destroyable via a self-contained swing-proximity check (the attack path
#     iterates the `enemies` array, so a decorative mesh would never be hittable).
gw = "  if (gauntletHasAffix('gravity')) { const pp = player.group.position; const d = Math.hypot(pp.x, pp.z); if (d > 1.5) { pp.x -= (pp.x / d) * 2.2 * dt; pp.z -= (pp.z / d) * 2.2 * dt; } }"
assert core.count(gw) == 1, "gravity-well anchor not found once in core"
totem = (gw +
    "\n  if (gauntlet.totem && !gauntlet.totem.dead) { const tt = gauntlet.totem, tp = tt.group.position, pp = player.group.position;"
    " if (player.swingT >= 0 && Math.hypot(pp.x - tp.x, pp.z - tp.z) < 3.4) { tt.hp -= player.dmg * dt * 3.5;"
    " if (tt.mesh && tt.mesh.material) tt.mesh.material.emissiveIntensity = 1.0 + Math.sin(game.time * 30) * 0.6;"
    " if (tt.hp <= 0) { tt.dead = true; detach(tt.group); addShock(tp.x, tp.z, 4, 0xff3a6a, 0.6, 0.2);"
    " floatText(tp.x, 3.2, tp.z, 'TOTEM DESTROYED', 'xp'); A.sfx.crit(); } } } // HASTE TOTEM: chip it down while swinging next to it")
core = core.replace(gw, totem)
# IMPORTANT: the pfx anchor is the LAST line INSIDE spawnBoss; append the function's closing brace
# to the anchor so the gauntlet subsystem lands AFTER spawnBoss at module/top level (not trapped inside it).
p.after(gnc["gauntlet_core"]["insertAfterAnchor"] + "\n}", core)

# ============================ SECTION 3: rift non-shared edits ============================
RIFT_SKIP = [
    "if (e.boss) {",                       # boss-block open (shared -> unified below)
    "YOU ARE A TRUE HERO",                 # boss-block close (shared -> unified below)
    "function directorUpdate(dt)",         # director gate (shared)
    "#mapoverlay'))) return;",             # touchmove exempt (shared)
    "stickers: game.stickers, questV: 7",  # save serialize (shared)
    "game.mgWins = d.mgw",                 # loadGame (shared)
    "e.target.closest('.btn')",            # mousedown + touchstart guards (overlap -> unified)
]
for e in rift["edits"]:
    if any(s in e["anchor"] for s in RIFT_SKIP):
        continue
    apply_edit(e)

# ============================ SECTION 4: gauntlet non-shared edits + gate build ============================
GAUNT_SKIP = [
    "game.state = 'dead';",                # death hook (shared)
    "if (e.type === 'usurper')",           # usurper + boss block (shared -> unified)
    "function directorUpdate(dt)",         # director gate (shared)
    "#mapoverlay'))) return;",             # touchmove exempt (shared)
    "showEnemyT: 0, minimapT: 0,",         # const game literal (shared -> unified)
    "stickers: game.stickers, questV: 7",  # save serialize (shared)
    "game.mgWins = d.mgw",                 # loadGame (shared)
    "e.target.closest('.btn')",            # mousedown guard (overlap -> unified)
    "e.target.closest('#mazepad')",        # touchstart guard (overlap -> unified)
]
for e in gaunt["edits"]:
    if any(s in e["anchor"] for s in GAUNT_SKIP):
        continue
    apply_edit(e)

# gate build (dropped from the revised newCode; reconstructed, banner pulsed via gauntletGateProps).
# Inserted after the town beacon line, inside buildTown (beacon/addPOI/root/colliders in scope).
GATE_BUILD = """
  // ----- Champions' Gauntlet arena gate (unoccupied town coord 6,-9) -----
  beacon(6, -9, 0xff5a4a);
  addPOI(6, -9, 'overworld', '⚔ GAUNTLET', '#ff7a5c');
  interactables.push({ x: 6, z: -9, zone: 'overworld', kind: 'gauntletgate', label: 'E — ENTER THE CHAMPIONS’ GAUNTLET' });
  colliders.push({ x: 5, z: -9.6, r: 0.45 }); colliders.push({ x: 7, z: -9.6, r: 0.45 }); // the two banner posts (approach at (6,-9) stays clear)
  (function gauntletGateProp() {
    const grp = new THREE.Group(); grp.position.set(6, 0, -9);
    const postMat = stdMat(0x2a1410, 0.85, 0, 0x180806, 0.2);
    const postGeo = new THREE.CylinderGeometry(0.16, 0.2, 3.4, 8);
    const pL = new THREE.Mesh(postGeo, postMat); pL.position.set(-1, 1.7, -0.6); pL.castShadow = true;
    const pR = new THREE.Mesh(postGeo, postMat); pR.position.set(1, 1.7, -0.6); pR.castShadow = true;
    const beam = new THREE.Mesh(new THREE.BoxGeometry(2.5, 0.22, 0.22), postMat); beam.position.set(0, 3.35, -0.6);
    const banner = new THREE.Mesh(new THREE.BoxGeometry(2.1, 1.5, 0.06),
      new THREE.MeshStandardMaterial({ color: 0x7a1410, emissive: 0xff3a18, emissiveIntensity: 0.7, roughness: 0.7 }));
    banner.position.set(0, 2.5, -0.62);
    grp.add(pL); grp.add(pR); grp.add(beam); grp.add(banner);
    root.add(grp);
    gauntletGateProps.push({ mesh: banner }); // pulsed each frame in updateAtmosphere
  })();"""
p.after("  beacon(doorX, doorZ, 0xffb86a);", GATE_BUILD)

# ============================ SECTION 5: unified shared edits ============================
# 5.1 usurper -> castleVictory: never for a gauntlet boss NOR a rift guardian
p.replace(
    "  if (e.type === 'usurper') setTimeout(castleVictory, 1300);",
    "  if (e.type === 'usurper' && !e.gauntlet && !e.riftGuardian) setTimeout(castleVictory, 1300);")

# 5.2 boss block OPEN: rift clear-detection + gauntlet self-contained carve-out + rift-guardian split
BOSS_OPEN_OLD = ("  if (e.boss) {\n    bossAlive = null; ui.bossplate.style.opacity = 0;\n"
                 "    game.tier++; game.powerMult *= 1.25;")
BOSS_OPEN_NEW = (
    "  if (e.riftFoe || e.riftGuardian) riftOnKill(e); // ASHEN RIFT: tier clear-detection + volatile death blast\n"
    "  if (e.gauntletAdd) { /* gauntlet broodlings / mirror clones: no plate, no tier bump, no defeat banner */ }\n"
    "  else if (e.gauntlet) { if (e === bossAlive) { bossAlive = null; ui.bossplate.style.opacity = 0; } } // CHAMPIONS' GAUNTLET: self-contained (gauntlet.power), never bumps global tier/powerMult\n"
    "  else if (e.boss) {\n"
    "    if (e.riftGuardian) { bossAlive = null; ui.bossplate.style.opacity = 0; banner(e.name.split(',')[0] + ' FALLS', 'the milestone breaks — descend or bank', false, 3.4); A.sfx.levelup(); }\n"
    "    else {\n"
    "    bossAlive = null; ui.bossplate.style.opacity = 0;\n"
    "    game.tier++; game.powerMult *= 1.25;")
p.replace(BOSS_OPEN_OLD, BOSS_OPEN_NEW)

# 5.3 boss block CLOSE: add the brace that closes the `else {` opened above (ASCII anchor, no em dash)
BOSS_CLOSE_OLD = ("    pfx.spawn(pos.x, 1.5, pos.z, { count: 120, vel: 5, velY: 7, life: 1.6, color: 0x9adf9a, color2: 0xffd040, mix: 0.5, grav: 5 });\n"
                  "    A.sfx.levelup();\n  }\n}")
BOSS_CLOSE_NEW = ("    pfx.spawn(pos.x, 1.5, pos.z, { count: 120, vel: 5, velY: 7, life: 1.6, color: 0x9adf9a, color2: 0xffd040, mix: 0.5, grav: 5 });\n"
                  "    A.sfx.levelup();\n    }\n  }\n}")
p.replace(BOSS_CLOSE_OLD, BOSS_CLOSE_NEW)

# 5.4 directorUpdate gate (both endgame modes own spawning)
p.replace(
    "function directorUpdate(dt) {\n  game.spawnT -= dt;",
    "function directorUpdate(dt) {\n  if ((typeof riftState !== 'undefined' && riftState.active) || (typeof gauntlet !== 'undefined' && gauntlet.active)) return; // endgame modes run their own spawners\n  game.spawnT -= dt;")

# 5.5 touchmove exempt chain: all three new overlays
p.replace(
    "(e.target.closest('#vendorpanel') || e.target.closest('#equippanel') || e.target.closest('.learning-overlay') || e.target.closest('#invpopup') || e.target.closest('#skillscreen') || e.target.closest('#stickerscreen') || e.target.closest('#mapoverlay'))) return;",
    "(e.target.closest('#vendorpanel') || e.target.closest('#equippanel') || e.target.closest('.learning-overlay') || e.target.closest('#invpopup') || e.target.closest('#skillscreen') || e.target.closest('#stickerscreen') || e.target.closest('#mapoverlay') || e.target.closest('#riftpanel') || e.target.closest('#riftchoice') || e.target.closest('#gauntletpanel'))) return;")

# 5.6 const game literal: gauntletBest (persisted) + gauntletPanel (transient). rift's riftState was
#     inserted after the closing brace in section 1, so this line is still intact.
p.replace(
    "  showEnemyT: 0, minimapT: 0,\n};",
    "  showEnemyT: 0, minimapT: 0, gauntletBest: { round: 0, kills: 0 }, gauntletPanel: false,\n};")

# 5.7 saveGame serialize: both new keys
p.replace(
    "stickers: game.stickers, questV: 7,",
    "gbest: game.gauntletBest, rd: riftDeepest, stickers: game.stickers, questV: 7,")

# 5.8 loadGame: restore both, default for old saves, clear any in-memory rift run on reload
p.replace(
    "    game.mgWins = d.mgw || {};",
    "    game.mgWins = d.mgw || {};\n"
    "    riftDeepest = d.rd || 1; // ASHEN RIFT deepest record (defaults for old saves)\n"
    "    game.gauntletBest = d.gbest || { round: 0, kills: 0 }; // CHAMPIONS' GAUNTLET best (defaults for old saves)\n"
    "    if (riftState.active) { riftState.active = false; riftState.awaitingChoice = false; riftState.runPower = 1; const _rp = $('riftplate'); if (_rp) _rp.style.opacity = 0; } // never resume a rift run across a reload")

# 5.9 gauntlet death hook (rift's death hook is a separate non-shared edit on the saveGame line)
p.after("  game.state = 'dead';",
        "\n  if (typeof gauntlet !== 'undefined' && gauntlet.active) gauntletEnd(false); // CHAMPIONS' GAUNTLET: dying ends the run (death screen stays; gauntletEnd guards the setZone)")

# 5.10 mousedown world-tap guard (3-line, desktop): exempt all three overlays
MD_OLD = ("  if (e.target.closest('.btn') || e.target.closest('#equippanel') || e.target.closest('#vendorpanel') ||\n"
          "      e.target.closest('#skillscreen') || e.target.closest('#skillhudbtn') || e.target.closest('#stickerscreen') ||\n"
          "      e.target.closest('.learning-overlay')) return;")
MD_NEW = ("  if (e.target.closest('.btn') || e.target.closest('#equippanel') || e.target.closest('#vendorpanel') ||\n"
          "      e.target.closest('#skillscreen') || e.target.closest('#skillhudbtn') || e.target.closest('#stickerscreen') ||\n"
          "      e.target.closest('.learning-overlay') || e.target.closest('#riftpanel') || e.target.closest('#riftchoice') || e.target.closest('#gauntletpanel')) return;")
p.replace(MD_OLD, MD_NEW)

# 5.11 touchstart world-interaction guard (long, with #mazepad/#joystick): exempt all three overlays
TS_OLD = ("  if (e.target.closest('.btn') || e.target.closest('#equippanel') || e.target.closest('#vendorpanel') ||\n"
          "      e.target.closest('#skillscreen') || e.target.closest('#skillhudbtn') || e.target.closest('#stickerscreen') ||\n"
          "      e.target.closest('.learning-overlay') || e.target.closest('#mazepad') || e.target.closest('#joystick') || e.target.closest('#mobtns') || e.target.closest('#skillbar') || e.target.closest('#invpopup')) return;")
TS_NEW = ("  if (e.target.closest('.btn') || e.target.closest('#equippanel') || e.target.closest('#vendorpanel') ||\n"
          "      e.target.closest('#skillscreen') || e.target.closest('#skillhudbtn') || e.target.closest('#stickerscreen') ||\n"
          "      e.target.closest('.learning-overlay') || e.target.closest('#mazepad') || e.target.closest('#joystick') || e.target.closest('#mobtns') || e.target.closest('#skillbar') || e.target.closest('#invpopup') || e.target.closest('#riftpanel') || e.target.closest('#riftchoice') || e.target.closest('#gauntletpanel')) return;")
p.replace(TS_OLD, TS_NEW)

# 5.12 breather-skip: DO during a Gauntlet breather summons the next champion early
p.replace(
    "function kbAttack() { // F is the DO button: talk > fight nearby danger > grab loot > swing\n  if (game.nearNPC && !game.vendorOpen) { openVendor(game.nearNPC.kind); return; }",
    "function kbAttack() { // F is the DO button: talk > fight nearby danger > grab loot > swing\n"
    "  if (typeof gauntlet !== 'undefined' && gauntlet.active && gauntlet.phase === 'breather') { gauntlet.breatherT = 0; return; } // DO during a Gauntlet breather summons the next champion early\n"
    "  if (game.nearNPC && !game.vendorOpen) { openVendor(game.nearNPC.kind); return; }")

# 5.13 expose the Gauntlet API on the debug hook (parity with rift; rift's __sanctum line was added in section 3)
p.replace(
    "      riftState, riftStart, riftDescend, riftClearTier, riftChoiceDescend, riftChoiceBank, riftOpenPanel, get riftDeepest() { return riftDeepest; },",
    "      riftState, riftStart, riftDescend, riftClearTier, riftChoiceDescend, riftChoiceBank, riftOpenPanel, get riftDeepest() { return riftDeepest; },\n"
    "      gauntlet, gauntletStart, gauntletEnd, gauntletSpawnRound, gauntletSpawnSuperboss,")

p.save()
