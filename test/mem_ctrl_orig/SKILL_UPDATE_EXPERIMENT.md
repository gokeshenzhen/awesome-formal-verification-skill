# mem_ctrl_orig — Skill-Update Experiment & Reproduction

Date: 2026-06-24

This file documents the work done **after** the original two-arm blind test
(`blind/no_skill`, `blind/skill`), i.e. the skill update for stalled-memory
abstraction and how to reproduce every result. Everything lives under
`test/mem_ctrl_orig/` (note: `test/` is gitignored by design — these are local
reproduction artifacts, not shipped content).

## What changed in the skill (committed, in git)

- `knowledge/fpv/complexity-management/abstraction.md` — Memory Abstraction now
  has a **stall trigger checklist**, a generic **black-box-one-array-instance +
  symbolic-slot reconnect recipe**, and a **signoff-discipline** note.
- `knowledge/fpv/complexity-management.md` — decision-tree + anti-pattern rows.
- `benchmarks/fpv/scenarios.{json,md}` — new control scenario
  `mem-abstraction-stall`.

Commit: `feat(fpv): add stalled-memory abstraction trigger`.

## Directory layout under test/mem_ctrl_orig/

```
simple_mem_design.sv          benchmark RTL (DUT) — never edited
mem_ctrl_top.sv               benchmark RTL (DUT) — never edited
README.md                     neutral task description given to agents
blind/no_skill/               original arm: no skill   (stalled on mem_works_ndc)
blind/skill/                  original arm: raw skill   (also stalled — the GAP)
blind/skill_abstraction_experiment/   <-- NEW blind validation run (see below)
oracle_reference/             my hand-written reference solution (hidden from the
                              blind agent during the test; kept for comparison)
benchmark_eval/               run_scenarios.sh output for mem-abstraction-stall
SKILL_UPDATE_EXPERIMENT.md    this file
```

## 1. Blind validation run (the real test of the updated skill)

`blind/skill_abstraction_experiment/` is the work of a **fresh sub-agent** that
was given ONLY the updated skill plus the realistic situation
("`mem_works_ndc` is undetermined after raw `prove -all`"), and was **not** told
to use memory abstraction. It independently abstracted and proved it.

Reproduce (re-run the agent's own scripts):
```bash
cd test/mem_ctrl_orig/blind/skill_abstraction_experiment
# the agent's final, working script is run_*/prove_mem_abstraction_v3.tcl
jg -no_gui run_20260624_185303/prove_mem_abstraction_v3.tcl
```
Result: `mem_ctrl_top.u_mem.mem_works_ndc` **proven** (AM engine, Infinite bound,
~0.08 s); flops 16,523 → 172; precondition cover hit (non-vacuous). Classified as
a **disclosed trusted-abstraction** result. See its `RESULT.md`.

## 2. Oracle reference solution (for comparison only)

`oracle_reference/` is the solution I wrote by hand to know what "correct" looks
like. It was deliberately stored outside the agent's read scope during the blind
test so it could not leak. Reproduce:
```bash
bash test/mem_ctrl_orig/oracle_reference/run.sh
```

## 3. Benchmark scenario eval (run_scenarios.sh)

`benchmark_eval/mem-abstraction-stall.txt` is the raw answer the skill-equipped
`claude -p` produced for the new scenario, graded concept 3/3, exact(JG) 1/1.
Reproduce:
```bash
bash benchmarks/run_scenarios.sh mem-abstraction-stall
```
(Requires the `claude` CLI on PATH and the skill installed via
`bash scripts/install.sh`. Output dir is /tmp by default; set OUT=... to relocate.)

## Integrity notes

- The two benchmark RTL files were never edited (verify: `git status` shows them
  unchanged; they are tracked outside the `test/` ignore via... actually `test/`
  is fully ignored, so confirm by diffing against the committed copies if needed).
- The blind run and the oracle both add a **disclosed** memory contract; neither
  is an unqualified raw-RTL signoff. To upgrade, discharge that contract against
  the real `mem_imp`.
- Do NOT cite the older `test/mem_abs` result as proof of the original `mem_imp`;
  it rewrote `simple_mem`.
