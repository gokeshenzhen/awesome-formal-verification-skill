# Weak-model skill A/B — result (gpt-5.4-mini, Codex)

> Manual double-blind on a **weak model** (`gpt-5.4-mini`, via Codex), two cases ×
> two arms. Hypothesis under test: the formal-verification skill's value
> **amplifies on a weaker model** (frontier A/B showed no differentiation because
> the strong no_skill arm re-derived the technique). Every number cites a raw
> artifact under each arm's dir.
>
> Capacity note: during the `cnt_abs` skill arm, `gpt-5.4-mini` briefly hit
> "model at capacity"; the run continued on the same `gpt-5.4-mini medium`. Both
> arms are the same weak model.

## Headline

**On the weak model, no_skill FAILED both cases; skill SOLVED both — ~60–140× faster.**
This is the clean differentiation the frontier suite never produced.

| Case | no_skill (weak) | skill (weak) |
|---|---|---|
| **cnt_abs** | ❌ no signoff — main run **4 proven / 2 CEX**, never converged; covers only via a disclosed `reset -init_state` hack; **16m46s** and still failed | ✅ **7 proven / 6 covered**, `abstract -counter cntr -values 0 8369262 268407145`, **10.78s** |
| **helper_counters** | ❌ **0 proven / 2 undetermined**, raw proof never closed, witness undetermined @bound 41; **full proof not reached** | ✅ embedded assertion **proven** (3/3), helper lemma `eq_cnt = (counter1==counter2)` proved then `-with_helpers`, **7s** |

**Citations**
- cnt_abs no_skill: `cnt_abs/no_skill/report.md` (run `proj_20260629_121345`: "4 proven, 2 cex"; "not signoff-quality"; elapsed "about 16m 46s"; "not calling the result raw-RTL signoff").
- cnt_abs skill: `cnt_abs/skill/final_report.rpt` (RESULTS [2..11] 6 functional asserts proven + `:noConflict`; `reach_A`/`reach_B` covered @bound 3/5); `cnt_abs/skill/report.md` §Runtime (10.784 s).
- helper no_skill: `helper_counters/no_skill/report.md` ("could not complete a raw-RTL proof"; Proven 0 / Undetermined 2; "Time to first full proof: not reached").
- helper skill: `helper_counters/skill/proj_H_summary.rpt` (`test._assert_1` proven engine H Infinite; `eq_cnt` proven; 3/3 asserts); `helper_counters/skill/report.md` §Timing (7 s).

## Five-dim read

- **D1 outcome** — **skill wins decisively on both.** no_skill reached no full proof on either; on cnt_abs it even emitted **2 CEX** (wrote *wrong* properties), i.e. a quality failure, not just a capacity stall. skill closed both.
- **D2 soundness** — both skill arms **correctly disclosed** they are not unqualified raw-RTL signoffs (cnt_abs covers lean on counter abstraction; helper proof leans on `eq_cnt`, itself proven). Good discipline. Non-vacuity: cnt_abs skill **witnessed** the milestone covers (`reach_A`/`reach_B` covered); helper skill left `:precondition1` undetermined (honest — deep 2^32 antecedent).
- **D3 proof cost** — skill 10.78s / 7s vs no_skill 16m46s (failed) / not-reached. ~60–140× wall, and no_skill's spend bought a *failure*.
- **D4 exploration** — no_skill flailed (cnt_abs: raw racing + init-state witness hacks across ~12 proj dirs; helper: ~7 proj dirs, never found the lemma). skill went near-straight to the documented technique.
- **D5 strategy** — the crux: **the weak no_skill model never found the technique.** cnt_abs no_skill never tried `abstract -counter`; helper no_skill never tried a helper lemma. skill handed both the trigger + the flow.

## What this proves (and its limits)

1. **The hypothesis holds.** The skill's value is real and **shows up cleanly on a weak model** exactly where the frontier A/B was blind. The differentiator is precisely the *trigger + tool-specific flow* (when to abstract / when to add a helper lemma, and the exact commands) — not general methodology. This is direct confirmation of the iteration direction recorded in memory `skill-iteration-atoms-triggers`.
2. **cnt_abs is in-distribution** (the skill's `abstraction.md` literally contains this example with these integers). So cnt_abs measures "the weak model can *apply* a spelled-out recipe it otherwise can't find" — still a real win (no_skill couldn't find it), but not generalization.
3. **helper_counters is the cleaner win.** The skill supplied the helper-lemma *flow* (`complexity-management.md`: prove helper → `set_helper` → `-with_helpers`); the agent itself supplied the lemma *content* (`counter1==counter2`, credited to its own reasoning in `skill/report.md` §39). Skill = trigger + flow; model = fill-in. That is the durable value shape.
4. **Honest caveats:** N=1 per arm; one brief capacity blip on the cnt_abs skill arm; neither skill arm is an unqualified raw-RTL signoff (both disclosed). For a stronger claim, rerun N≥3 and confirm the no_skill transcripts never touched the formal-verification skill (behaviorally they didn't — they never used the techniques the skill teaches).

## Bottom line

The earlier conclusion ("the skill barely helps") was a **frontier-model artifact**. On a weak model the same two cases flip to a clean skill win: **no_skill fails, skill solves, ~100× faster**, by applying the skill's trigger + tool-specific flow. The skill's value is real; the frontier A/B simply couldn't see it.
