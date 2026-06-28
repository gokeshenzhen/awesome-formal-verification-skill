---
name: blind-ab
description: >-
  Run an enforceable double-blind A/B experiment to measure whether the
  formal-verification skill actually helps an agent on a JasperGold FPV task.
  Use whenever the user asks to run a blind test, skill A/B, no_skill vs skill
  comparison, double-blind skill validation, or to benchmark/score the
  formal-verification skill — including Chinese phrasings ("双盲测试", "盲测",
  "skill 对照实验", "no_skill 对比", "验证 skill 有没有用"). Loads the protocol
  and drives benchmarks/blind_ab.sh so the run is isolated, leak-free,
  auditable, and written back to EXPERIMENT_REPORT.md.
---

# Blind A/B skill-validation router

You are about to run a skill-effect experiment. **Compliance is not optional and
not by memory.** Before doing anything else:

1. **Read the protocol** `test/BLIND_TEST_PROTOCOL.md` — Part I (neutrality /
   no-leak) and Part II (enforcement, audit, dimensions, write-back). Follow it.

2. **Drive it through the runner**, do not hand-roll the mechanics:
   - `benchmarks/blind_ab.sh init <case_dir> <top_module>` — scaffold sandboxes,
     manifest (RTL sha256 / jg version / skill commit), neutral README, leak scan.
     `<case_dir>` MUST be outside the skill repo (no relative path to knowledge/).
   - (write a neutral per-arm prompt to `<case>/.blind_sbox/{ns,sk}_prompt.txt`;
     for open-ended cases the generic template may not fit — keep it leak-free.)
   - `benchmarks/blind_ab.sh run <case> <top> ns|sk claude|codex [budget_sec]` —
     real background launch with PID file + budget + transcript capture. Each arm
     is an isolated `claude -p`/`codex exec` with its own agent-home sandbox
     (skill present for sk, absent for ns).
   - `benchmarks/blind_ab.sh watch <case>` — live per-arm progress (running?, wall,
     #tcl, #jg runs, latest proven/cover counts, RESULT.md). Loop it to monitor.
   - `benchmarks/blind_ab.sh stop  <case> [ns|sk]` — safe stop of an arm's process
     group (no pkill self-match).
   - `benchmarks/blind_ab.sh launch <case> <top> ns|sk claude|codex` — DRY-RUN that
     only prints the command (use `run` to actually execute).
   - `benchmarks/blind_ab.sh leakcheck <case>` — the no_skill transcript MUST show
     zero skill-path hits, else that arm is invalid.
   - `benchmarks/blind_ab.sh replay <case>` — Option-A cold replay of each arm's
     final script for fair, comparable engine-time.

   **Visible + stoppable runner pattern (recommended):** the SOLVING arms must stay
   isolated CLI processes (a sub-agent cannot structurally hide the globally
   installed skill from the no_skill arm — that would break the blind). To give the
   user live visibility and a stop control, run THIS orchestration as a watchable
   runner (a sub-agent or a foreground loop) that calls `run` for both arms then
   loops `watch`, reporting progress and honoring the per-arm `budget`. The user
   watches the runner and can `stop` either arm at any time. Do NOT make an arm
   itself a sub-agent.

3. **Never leak the technique.** The benchmark prompt/README/source/dir names must
   not name CAG, proof_structure, helper, invariant, abstraction, stopat, etc.
   Same neutral prompt for both arms; the only difference is skill access.

4. **Judge on the 5 pre-registered dimensions** (protocol Part II §4): D1 outcome
   (on propagated ROOT if decomposed), D2 soundness/non-vacuity, D3 proof-artifact
   cost (replay wall + max IPF057), D4 exploration cost, D5 strategy choice.
   Both arms full-proving is normal — the signal is D3/D4/D5. **no_skill winning is
   a valid finding; be willing to downgrade the case.**

5. **Every number must cite its raw artifact** (log path / IPF057 quote /
   transcript path / sha256). A bare number with no source is not auditable.

6. **Write back**: append a dated, fully-sourced section to the case's
   `EXPERIMENT_REPORT.md` (worked example: §12 of
   `test/marble_transfer_orig/EXPERIMENT_REPORT.md`).

Caveats (protocol Part II §6): N≥3 runs/arm (agents are stochastic); same
model/budget/machine for both arms; drop idle wall-clock gaps; the grader should
be a third context, not a solving agent.
