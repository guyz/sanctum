# Fix Brief — Brannic's Learning Mini-Games (hand this to a strong coding agent)

## Role & goal

You are a senior front-end engineer **and** an early-childhood learning-design specialist. Your job is to fix a suite of **logic / math / IQ puzzle mini-games built for a ~7-year-old (early or non-reader)**. They live in a single self-contained file:

`sanctum-of-ash.html` → the `<script id="minigames">` block (lines ~8806–12050).

Live screenshots of every game (one PNG per game id) are in the `screenshots/` folder next to this file — review them for the visual bugs; they show exactly what a child sees.

The games are reached in-game from Brannic the Innkeeper. **Several are confusing even to adults** because they are either **visually wrong** (the render contradicts the intended puzzle) or **logically off** (the "correct" answer is ambiguous, the rule is invisible, distractors are invalid, or difficulty is wildly age-inappropriate).

Below is a **verified audit** (every item was independently confirmed against the code). Fix **all** of them in one pass. Treat this as a single coordinated change: many issues share root causes (label/content mismatch, invisible rules, age-inappropriate difficulty, a couple of true rendering bugs), so fix the root cause, not just the symptom.

> The two genuinely **clean** games are **Coin Counting** and **Memory Cards** — use them as the quality bar for the others.

---

## Guiding principles (apply everywhere)

1. **Non-readers first.** A 7-year-old may not read. Any rule that can *only* be understood by reading a word (e.g. the category name "tool") is broken. Make the rule **visible** (color-coded groups, a legend, consistent iconography) and/or **spoken** (the framework has an `audioPrompt` field that is currently unused).
2. **One rule, one answer, unambiguous.** At the guided/tier-0 level, each puzzle must have exactly **one** defensible answer. If a distractor satisfies a *second* valid pattern, it's a bug.
3. **The picture must match the truth.** What is drawn must equal the underlying data: pip-dots must equal the number; the answer icon must visually belong to the clue group; "same shape, different fill" must still read as the same shape.
4. **Name = content.** The inn label (`MG_LIST`), the game title, and the actual puzzle must agree. Don't promise "gems" / "rotation" / "weighing" and deliver something else.
5. **Age-appropriate difficulty ladder.** Tier 0 (ages 6–7, "guided") must be small and gentle. Prefer fewer cells, fewer simultaneous visual dimensions, larger shapes, and concrete (countable) representations.
6. **Multi-select needs feedback.** If a child selects multiple cells, each selection must be **obviously** marked, and there should be no harsh all-or-nothing failure with no indication of what was wrong.

When you change a label/title/prompt, keep them consistent across `MG_LIST` (≈16584), the game's `title`/`demoText`, and `promptForItem`.

---

## Verified bugs to fix, by game

Severity: **H** = makes a game confusing/unsolvable/broken; **M** = materially misleading; **L** = polish.
Line numbers are approximate anchors in `sanctum-of-ash.html` — confirm in the source.

### A. Pathfinder (`path_maze`)

- **[M] Misleading "shortest path" framing.** Prompt (≈11183) says *"Find the shortest exit path"* and the explanation says *"without extra turns"*, but the game accepts **any** path within `maxMoves = bestMoves + ~8` (≈11201, 11260). A child who reaches the goal in 27/optimal-22 thinks they failed. **Fix:** reword to *"Escape the maze!"*; do not imply optimality.
- **[M] Move counter reads like a loss.** Counter shows `moves / bestMoves` (≈11213), so reaching the goal in 25 with best 23 shows "25 / 23". **Fix:** show `moves / maxMoves` (the actual budget) so the child sees they're within range.
- **[M] Maze far too large for the age.** Tier sizes are **17×17 / 25×25 / 33×33** (289 / 625 / 1089 cells), ~90 s budget, and `openLoopPaths` removes ~18 walls. A 7-year-old can't plan this. **Fix:** reduce `TIER_SIZES` to roughly **[9, 13, 17]** (and/or raise the time budget).
- **[H] Unreadable on mobile.** CSS caps the maze at `min(620px, 84vw)` (≈5315); a 33×33 maze on a 375px phone is ~8px/cell (markers invisible, text overflows). **Fix:** cap maze size on small viewports (the [9,13,17] change above largely resolves this; also ensure min cell size / hide overflow text).
- **[M] Hint points backward on alternate optimal paths.** Loops create multiple shortest paths; the hint assumes the child is on the *stored* `round.path` (≈11235–11238). If they take a different optimal path, `indexOf` returns −1 → `pathIndex = 0` → it glows the first cells (toward the start). **Fix:** recompute the shortest path **from the player's current cell** to the goal each time the hint is shown.

### B. Signal Sprint (`gem_line`)

- **[M] Inn label lies.** `MG_LIST` (≈16588) sub is *"spot the matching gems"* but the game (`Signal Sprint`) has no gems — it's abstract shapes/symbols. **Fix:** change the sub to e.g. *"match the signals"*.
- **[H] Hollow shapes read as a different object ("moon phases").** For tier 1+, the "one feature off" distractor can flip `fill` to `hollow` (≈9080, 9112). A hollow circle renders as a ring/crescent (≈4848–4851) and a child sees a *different thing*, not "same shape, different fill." (This is exactly why the live screenshot looked like moon phases.) **Fix:** for ages 6–7, **disable `hollow` fill** in `symbol_search` (keep `fill:'solid'`); only introduce solid/hollow later with an explicit "these are both circles" legend.
- **[H] `symbol_coding` requires literacy under time pressure.** It shows a number→symbol key and asks the child to look up 1–2 **numerals** and pick the symbol sequence (≈10130–10168), with reversal/wrong-entry distractors. A non-reader can't do numeral substitution against a clock. **Fix:** either drop `symbol_coding` from this game for the young tier, or restrict to a single-number lookup (codeLength 1) with a small key and dot-count number cues.
- **[H] Cancellation/search targets are perceptually confusable.** Targets are drawn from `sun/moon/star/leaf/drop/bolt/key/gem` (≈10174); sun/star/leaf look alike at small sizes, with no slow target reveal, in 12–20 cells in ~95 s (≈10101). **Fix:** show the target alone for ~2–3 s before the grid appears, and/or use more visually distinct icons (sun, heart, lightning, tree, door).
- **[H] Multi-select has no per-click feedback.** Clicking a cell only toggles `selectedIds`; the `.selected` style is a near-invisible darkening on a dark bg, and correctness is shown only after "Seal" (≈10881–10948). The child can't tell what they've picked. **Fix:** mark selected cells boldly (checkmark + clear highlight), keep an "X / Y chosen" counter, and don't fail silently — indicate which were wrong (or allow easy deselect before sealing).
- **[M] Tier-2 symbol_search has 6 simultaneous dimensions.** shape×color×count×fill×rotation×sign all vary (≈10097–10127) with no legend. Too much for the age. **Fix:** at the young tier restrict to shape+color+count; add fill/rotation only later, with explicit teaching.

### C. Pattern Forge (`rune_matrix`)

- **[H] Ambiguous competing-rule distractor.** In `buildPatternSeries` (≈9619) a distractor is `applyRule(answer, nextRuleInCycle)`. For a color sequence, this yields e.g. *violet triangle ×2* — which satisfies **both** "color advances" *and* "count increases", so the child's reasoning is valid but marked wrong. **Fix:** for tier 0, generate distractors that only change a **non-sequence** feature (e.g. `shape` or `fill`), never one that forms a second consistent rule; or detect-and-skip any distractor that extends a valid rule.
- **[H] Arbitrary color order.** `IQ_COLORS` cycles gold→blue→green→red→violet (≈9043–9057). A child sees blue→green→red→? and has no way to know "violet" comes next (it's not the rainbow, not light→dark). **Fix:** at tier 0 avoid color-progression sequences (use shape/count/rotation), or use a 2-color alternation, or show a visible color-ladder legend, or reorder `IQ_COLORS` to a familiar rainbow.
- **[M] One title, four different puzzle types.** Each round randomly picks matrix / analogy / classification / series with the constant title "Pattern Forge" (≈11319–11333), and tier-0 can already hit a **2-rule** 3×3 matrix. **Fix:** gate families by tier (tier 0 → `pattern_series` only; add matrix/analogy later), and/or show an on-screen puzzle-type label when the family changes; consider renaming to a generic "Rune Lab".
- **[M] Stacked multi-shape rendering hurts discrimination.** `count>1` stacks small (~25px) shapes (≈9092–9100); triangle vs diamond at that size with no outline is hard. **Fix:** render counts **side-by-side**, enforce a larger min shape size at tier 0, add outlines, cap tier-0 count at 2.
- **[M] Tier-0 series shows only 2 example steps.** `length=4` (show 3, hide 1) gives only two transitions to infer the rule (≈9609). **Fix:** use `length=5` at tier 0 (3 transitions) so the rule is unambiguous.
- **[L] Feedback never identifies the correct option;** distractor rationales are generic (≈9622, 9630–9634) and the `wrongAnswerRationales` array is unused. **Fix:** name the answer in the explanation (and/or use `audioPrompt`), and differentiate the rationale per distractor type.

### D. Clue Cards (`clue_cards`) — *the most confusing game*

- **[H] The answer's icon contradicts its category.** Matching is by **semantic category string** (e.g. category="tool"), but each item renders its `sign` (≈10421), and `lamp.sign='sun'`, `lock.sign='key'`, etc. So the *correct* answer for "tool" can render as a **sun**, while the clues render as keys — there is **no visual relationship** between clue and answer (≈9297–9301, 10246–10251). This is why the puzzle is unsolvable by looking. **Fix (pick one):** (a) give every item a **category-consistent** visual marker (e.g. all "tool" items share a badge/color), or (b) switch the matching rule to something **visually coherent** (match by color, shape, or count, where visual similarity *is* the rule), or (c) add an explicit icon→category legend.
- **[H] Text-only prompt for non-readers.** Prompt is `Choose something from <value>` with a bare word like "tool" (≈10257–10261, 10724). A non-reader can't use it. **Fix:** make the prompt visual ("find one like these" pointing at enlarged clues), and/or speak it.
- **[M] Distractors can reuse a clue's exact icon.** Distractor pool only filters by *category* (≈10245), not by icon, so the same `sign` can appear both as a clue and as a wrong choice. **Fix:** exclude any distractor whose `sign` matches any clue's `sign`.
- **[M] Abstract semantic categorization is developmentally too hard here** without visual scaffolding (the ageBand is "6-7 guided", ≈9361). **Fix:** add color-coded category grouping / a legend, or reduce tier-0 to a visual rule (color/shape/count).
- **[L] Feedback assumes the category is obvious** ("does not match the direction" ≈10252; "compare the clue pictures" ≈10777). **Fix:** state the unifying property and make it visible.

### E. Bridge Rotation (`shape_forge`)

- **[H] Title misrepresents the game.** Title is "Bridge Rotation" (≈11298) but rounds are ~⅓ rotation, ~⅓ paper-folding, ~⅓ assembly (≈11301). **Fix:** rename to "Bridge Puzzles" / "Shape Challenges", and make `MG_LIST`, `title`, `demoText`, and `promptForItem` consistent.
- **[M] "Unfold" vs "fold in your mind" conflict.** `demoText` says *"Turn, fold, or build … in your mind"* (≈11303) while the folding prompt says *"Unfold the bridge plan"* (≈11306). **Fix:** unify the metaphor (e.g. prompt "Show where all the holes appear"; demo "imagine unfolding the paper").
- **[M] Paper-folding shows a lone cell with no scaffolding.** A single filled cell in a 4×4 grid (≈10566) with only abstract text gives the child no way to grasp "folded → hole → unfolded" — and one distractor is the identical single cell. **Fix:** draw the fold line(s), label "folded paper", optionally show folded vs unfolded side by side.
- **[M] Multi-select rotation isn't checked for rotational symmetry.** At stretch tier two rotations are marked correct (≈9780–9787); if the shape is rotationally symmetric, the two "correct" options render **identically** → unwinnable. **Fix:** after choosing the two correct turns, re-roll if `rotateCells(target,t1)` equals `rotateCells(target,t2)`.
- **[L] Mixed metaphors** ("plate" / "plan" / "pieces", ≈11304–11308) make it feel like three unrelated games. **Fix:** use a consistent noun/verb framing.

### F. Scale Riddles (`make_target`)

- **[H] Pip-dots capped at 10 but answers reach 12.** `renderNumber` caps dots at `Math.min(10, value)` (≈10431), but `buildNumberSeries` tier 1 (`[4,6,8,10,12]`) and `buildNumberAnalogy` ×2 (c=6) produce **12**. The number reads "12" while only **10 dots** show → the child counts 10 and is misled (this is the pip mismatch seen in the screenshot). **Fix:** raise the cap to ≥14 (and render >10 as legible groups, e.g. two rows of dots / a 5+5+remainder layout), **or** clamp generators so answers ≤10 at the young tier.
- **[M] Number-analogy ×2 can exceed the pip cap** (same root cause; ≈9729–9757). **Fix:** covered by the cap change, or restrict ×2 to `c ≤ 5` at the young tier.
- **[L] "Scale Riddles / weigh, count, compare" is misleading** — ¾ of rounds are number puzzles, not weighing (≈ families list). **Fix:** rename to something content-neutral (e.g. "Mind Trials"), or gate families so the title fits, or split per family.

### G. Memory Garden (`memory_match`) — hidden game

- **[H] Unreachable.** Registered in `LEARNING_GAMES` (≈11643) but **absent from `MG_LIST`** (≈16584). **Fix:** either add it (`{ id:'memory_match', icon:'🌸', name:'Memory Garden', sub:'remember the symbol pairs' }`) **after** fixing the bug below, or remove it from `LEARNING_GAMES` if not intended for release.
- **[H] Tier 1+ is impossible — variants aren't rendered.** Tier 1+ creates "plain" vs "outline" card variants (≈10067), but `renderMemoryMatching` calls `renderSign(card.sign)` and ignores `variant` (≈9104, 10636) — both render identically, so the child can't tell the two "suns" apart. **Fix:** render the variant visually (e.g. outline cards get a dashed border / hollow fill), or drop variants and use distinct symbol pairs.
- **[M] Multi-select feedback is opaque** ("Look again. The answer stays hidden until the next miss." ≈10949) and the study board isn't re-shown. **Fix:** say "both cards must show the same symbol" / "choose 2 cards first", and show a reference or symbol-count hint.

### H. Shared IQ framework (affects multiple games) — defensive

These are **latent/defensive** (the current generators avoid triggering them via unique keys, so they are lower user-impact — but worth hardening while you're in here):

- **[M] No runtime validation of generated items.** `verifyIqItem`/`assertValidIqItem` exist (≈10308–10370) but are **never called**. A malformed item (0 correct choices, count mismatch) would propagate silently. **Fix:** call `assertValidIqItem(item)` at the end of `attachChoices` (≈9407) (throw or regenerate on failure) so any generator regression is caught.
- **[M] `makeChoices` dedups purely by key.** It removes duplicate-keyed choices without considering the `correct` flag (≈9383–9391). Today generators include unique indices in keys so it doesn't bite, but it's fragile. **Fix:** after dedup, assert `choices.length >= expected` and that the correct count matches `answerMode`; never silently under-fill.
- **[L] Inconsistent difficulty across families** — e.g. analogy keeps 4–5 choices at all tiers while symbol_search jumps 12→16→20 cells (≈9514, 10101). **Fix:** normalize per-tier choice/scan counts across families so "tier 0" means the same load everywhere.

---

## Do NOT chase these (investigated, confirmed NOT bugs)

So you don't waste effort re-deriving them:

- The `makeChoices` dedup **does not** currently drop a correct answer or cause off-by-one IDs in multi-select grids — all multi-select generators put a **unique index in the choice key** (`"${index}_${itemKey(cell)}"` etc.), so identical visuals get distinct keys and both survive with `correct:true`. (Still worth the defensive assert in H, but there's no live failure.)
- Paper-folding "wrong-axis" distractors **cannot** collide with the correct unfolding — single-axis folds yield 2 cells, dual-axis yield 4; different cardinality ⇒ different `cellsKey`.
- Scale Riddles pip-dots **do not** get clipped by overflow — the containers are `overflow: visible` with no height cap; the only real pip issue is the **count cap of 10** (bug F1).
- Memory Garden's title isn't internally inconsistent today (it's simply not wired into the menu) — the real issues are unreachability + the variant render bug.

---

## Acceptance criteria

When done, for **every** game at the **guided (tier-0)** level:
1. The inn label, title, demo text, and prompt all describe the **same** activity.
2. A non-reader can understand the goal from **visuals/audio alone** (no required word-reading).
3. There is exactly **one** correct answer and no distractor forms a second valid rule.
4. The rendering matches the data (pip count = number; answer icon visibly belongs to the clue group; "same shape/different fill" still reads as the same shape).
5. Multi-select shows clear per-selection feedback and never fails silently.
6. Difficulty is gentle (small mazes/grids, ≤3 visual dimensions, large shapes, countable numbers ≤10 at tier 0).
7. `Memory Garden` is either correctly listed **and** playable at all tiers, or removed.
8. `assertValidIqItem` runs on generated items and nothing throws across a few hundred seeds per family.

**Verify** by launching each game across several seeds/tiers (you can construct a `LearningSubsystem` and call `startMoment({preferredMiniGames:[id], roundCount, seed})`, or click through Brannic in-game) and confirming a child could reasonably solve tier-0 rounds. Keep Coin Counting and Memory Cards as the reference standard. Make the changes surgically within `<script id="minigames">` (and the `MG_LIST` entries near line 16584); don't regress the two clean games.
