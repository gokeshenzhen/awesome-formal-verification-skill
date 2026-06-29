# Memory Controller Original-RTL Blind Test Report

Date: 2026-06-24

This report records a neutral two-arm experiment for:

```text
test/mem_ctrl_orig/simple_mem_design.sv
test/mem_ctrl_orig/mem_ctrl_top.sv
```

The design keeps the real `mem_imp` array implementation and wraps it with a
small controller. Unlike the earlier `mem_abs` archive, this experiment forbids
rewriting `simple_mem` or `mem_imp` as the final design under test.

## Agent Access Rules

| Agent | Skill Access | Forbidden Inputs |
|---|---|---|
| NS | No formal skill | `knowledge/`, `adapters/`, `tool-specific/`, `raw-docs`, `extractions`, previous testcase directories, previous blind reports |
| SK | Formal skill allowed | `test/mem_abs`, `test/cag_counters`, prior blind reports, `raw-docs`, `extractions`, solution archives |

## Signoff Rule

A full raw-RTL result must analyze the benchmark RTL files from this directory
and prove the target assertions on `mem_ctrl_top`.

Any result that depends on modeling assumptions beyond the benchmark RTL itself
must disclose those assumptions and must not be labeled as an unqualified proof
of the original RTL.

## Agent Results

| Agent | Skill Access | Strategy | Best Run | Result |
|---|---|---|---|---|
| NS | No | Raw RTL, focused top target; separate raw `prove -all` attempt | `blind/no_skill/runs/20260624_165725` focused, `blind/no_skill/runs/20260624_165306` raw | Top controller assertion proven; full all-assertion raw proof not achieved |
| SK | Yes | Raw RTL canonical setup with sanity/dead-end checks and engine tuning | `blind/skill/runs/20260624_165452_raw` | Top controller assertion proven; full all-assertion raw proof not achieved |

Neither agent edited or replaced the benchmark RTL files. Neither agent added a
trusted memory model, bind helper, stopat, black-box reconnect, or other
modeling assumption.

## No-Skill Agent

Workspace:

```text
test/mem_ctrl_orig/blind/no_skill
```

Key scripts:

```text
run.sh
prove_top_targets.tcl
prove_raw.tcl
RESULT.md
```

The focused default run analyzes the benchmark RTL unchanged:

```tcl
analyze -sv09 "$bench_dir/simple_mem_design.sv" "$bench_dir/mem_ctrl_top.sv"
elaborate -top mem_ctrl_top
clock clk
reset rst
prove -property {mem_ctrl_top.ctrl_readback_ok}
prove -property {mem_ctrl_top.ctrl_transaction_seen}
```

Result from `runs/20260624_165725`:

```text
mem_ctrl_top.ctrl_readback_ok: proven in 85.96 s
mem_ctrl_top.ctrl_transaction_seen: covered in 4 cycles
```

The raw all-property run:

```bash
bash test/mem_ctrl_orig/blind/no_skill/run.sh prove_raw.tcl
```

preserved result in `runs/20260624_165306`:

```text
assertions: 2 total
  proven: 1
  undetermined: 1
covers: 3 total
  covered: 3
```

The unresolved assertion was:

```text
mem_ctrl_top.u_mem.mem_works_ndc
```

The precondition cover for that assertion was covered, so the property was not
vacuous. The proof did not close before interruption.

## Skill Agent

Workspace:

```text
test/mem_ctrl_orig/blind/skill
```

Key scripts:

```text
run.sh
jg_raw.tcl
jg_focused.tcl
RESULT.md
```

The corrected raw run analyzes the benchmark RTL unchanged:

```tcl
analyze -sv \
  /home/robin/Projects/awesome-formal-verification-skill/test/mem_ctrl_orig/simple_mem_design.sv \
  /home/robin/Projects/awesome-formal-verification-skill/test/mem_ctrl_orig/mem_ctrl_top.sv
elaborate -top mem_ctrl_top
clock clk
reset rst
prove -all
```

Additional setup used:

```text
sanity_check
visualize -reset
check_assumptions
check_assumptions -dead_end
set_prove_advanced_simplification on
set_word_level_reduction on
set_proofmaster on
```

Observed setup facts from `runs/20260624_165452_raw`:

```text
Flops: 516 (16523)
Embedded assumptions: 2
Embedded assertions: 2
Embedded covers: 3
sanity_check: clean
check_assumptions: no conflict
check_assumptions -dead_end: no dead end
```

Reached proof results before stop:

```text
mem_ctrl_top.ctrl_readback_ok: proven in 31.02 s
mem_ctrl_top.ctrl_transaction_seen: covered in 4 cycles
mem_ctrl_top.u_mem.mem_works_ndc:precondition1: covered in 4 cycles
mem_ctrl_top.u_mem.mem_works_ndc: not proven at stop time
```

The run stopped before post-proof summary reports were generated, but the log
shows engines repeatedly working on `mem_ctrl_top.u_mem.mem_works_ndc` with no
counterexample and no proof.

## Interpretation

This experiment fixes the flaw in the earlier `mem_abs` archive. The agents did
not prove a rewritten `simple_mem`; they both analyzed the benchmark RTL files
containing the real `mem_imp` array.

The outcome is:

- Both agents can prove the external controller property on raw RTL.
- Neither agent full-proved every embedded assertion, because the internal
  original memory property `u_mem.mem_works_ndc` remained unresolved.
- The skill agent produced a cleaner canonical FPV setup and proved the top
  controller assertion faster in the observed run, but it did not apply a
  disclosed memory abstraction or close the hard internal memory assertion.

Therefore this is a better experiment for design-integrity discipline, but it
does not yet demonstrate a successful skill-assisted full proof. A follow-up
should allow or request a disclosed trusted memory abstraction/reconnect flow
and then score whether the skill agent uses it correctly without replacing the
whole DUT.

## Follow-Up: Skill Update + Reproducible Disclosed Abstraction (2026-06-24)

The follow-up above was done. Root cause of the stall: the skill held the
memory-abstraction atoms only as a *static reference* — no stall trigger, no
inner-instance recipe, no signoff-discipline note — so neither arm connected
"`mem_works_ndc` undetermined" to "abstract the array now."

Skill fix (committed): `knowledge/fpv/complexity-management/abstraction.md`
gained a stall **trigger checklist**, a generic **black-box-one-array-instance +
symbolic-slot reconnect** recipe, and a **disclosed-trusted vs raw-RTL signoff**
note; `complexity-management.md` got matching decision-tree / anti-pattern rows.

Blind validation (third arm, `blind/skill_abstraction_experiment/`): a fresh
agent given **only** the updated skill — and **not** told to use memory
abstraction — independently:

- black-boxed only the array instance: `elaborate -top mem_ctrl_top -bbox_i {u_mem.m1}`
- bound a single-slot tracker (`mem_slot_bind.sv`) keyed to the symbolic `ndc_addr`
- reconnected the boxed read with a disclosed contract
  (`assume {u_mem.u_abs.rd_ndc_q |-> u_mem.m1.dout == u_mem.u_abs.tracked_q}`)
- covered the precondition (non-vacuous) and ran `prove -all`

Result (JasperGold 2025.12p002, reproduced):

```text
flops: 16,523 → ~109 after bbox (512x32 mem_content array removed)
mem_ctrl_top.u_mem.mem_works_ndc : proven (engine AM, ~0.05-0.08 s)
mem_works_ndc:precondition1      : covered (non-vacuous)
ctrl_readback_ok                 : cex UNDER THIS ABSTRACTION (expected — the
                                   contract constrains reads only at ndc_addr;
                                   it is proven on full raw RTL in the other arms)
```

Classification: **DISCLOSED TRUSTED-ABSTRACTION RESULT**, not a raw-RTL signoff.
The reconnect `assume` is trusted (assumed, not discharged against the real
`mem_imp`). To upgrade to full raw-RTL signoff, prove that contract as an
assertion against `mem_imp`, or supply an equivalence argument.

Reproduce (same launcher convention as `no_skill` / `skill`):

```bash
cd test/mem_ctrl_orig/blind/skill_abstraction_experiment
./run.sh        # → runs/<timestamp>/prove_summary.rpt
```

Caveat preserved: this still does **not** make the old `test/mem_abs` result a
proof of the original `mem_imp` (that experiment rewrote `simple_mem`). And the
original two arms remain the record that a *raw* `prove -all` does not close
`mem_works_ndc` on the unchanged array. See `SKILL_UPDATE_EXPERIMENT.md` for the
full layout (oracle reference, benchmark eval, archived original agent run).
