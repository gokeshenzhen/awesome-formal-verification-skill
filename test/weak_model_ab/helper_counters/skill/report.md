# two_counters JasperGold Report

## Outcome

- Embedded assertion proven: `@(posedge clk) &counter1 |-> &counter2`
- Helper lemma used: `eq_cnt` proved first, then imported with `-with_helpers`
- Non-vacuity witness: `test._assert_1:precondition1` remained `undetermined`
- Raw-RTL unqualified proof: `no`

## How The Proof Was Reached

1. I analyzed and elaborated [`two_counters.v`](/home/robin/Projects/awesome-formal-verification-skill/test/weak_model_ab/helper_counters/two_counters.v) as `test`, clocked on `clk`, reset on `rst`, and ran `sanity_check` plus `check_assumptions`.
2. Direct proof attempts with `N` and `M` stalled in trace search and did not close the embedded assertion cleanly.
3. I introduced a helper assertion:
   - `assert -helper -name eq_cnt { @(posedge clk) counter1 == counter2 }`
4. I proved that helper first.
5. I then activated it with `assert -set_helper eq_cnt` and proved the embedded assertion with `prove -with_helpers -property {<embedded>::test._assert_1}`.
6. The safety proof closed immediately under engine `H`.
7. I separately tried to prove the auto-generated antecedent witness cover `test._assert_1:precondition1`; it stayed `undetermined`, so I could not formally demonstrate non-vacuity.

## Skill Knowledge Used

- [`knowledge/fpv/workflow.md`](/home/robin/Projects/awesome-formal-verification-skill/knowledge/fpv/workflow.md)
  - Contributed the required JasperGold stage order: `clear -> analyze -> elaborate -> clock/reset -> sanity -> prove -> report`.
  - Contributed the batch-flow discipline and the need to keep the project under `skill/`.
- [`knowledge/fpv/tcl-commands.md`](/home/robin/Projects/awesome-formal-verification-skill/knowledge/fpv/tcl-commands.md)
  - Contributed the Tcl scripting pattern for scripted Jasper runs and the `report -summary -result -force` form.
  - Contributed the clarification that Jasper Tcl is not plain Tcl in a few places.
- [`knowledge/fpv/property-writing.md`](/home/robin/Projects/awesome-formal-verification-skill/knowledge/fpv/property-writing.md)
  - Contributed the clocked SVA framing for the helper lemma and the embedded assertion.
  - Contributed the formal-friendly reading of `|->` on a single clock.
- [`knowledge/fpv/engine-tuning.md`](/home/robin/Projects/awesome-formal-verification-skill/knowledge/fpv/engine-tuning.md)
  - Contributed the engine selection guidance.
  - I used that guidance to stop re-racing `N`/`M` and switch to `H` once the helper lemma was available.
- [`knowledge/fpv/complexity-management.md`](/home/robin/Projects/awesome-formal-verification-skill/knowledge/fpv/complexity-management.md)
  - Contributed the helper-lemma flow: prove the helper first, then activate it with `assert -set_helper`, then prove the target with `-with_helpers`.
  - Contributed the rule that helpers must be proven before use.

My own contribution was the proof-shape choice: `counter1 == counter2` is the right inductive lemma for this DUT, because both counters are updated identically from the same reset state.

## Exact JG Commands

Final proof run:

```bash
jg -fpv -batch -no_jges -proj skill/proj_H_20260629_135202 -tcl skill/proj_H.tcl
```

Contents of `skill/proj_H.tcl`:

```tcl
clear -all
analyze -sv two_counters.v
elaborate -top test
clock clk
reset rst
sanity_check
check_assumptions
assert -helper -name eq_cnt { @(posedge clk) counter1 == counter2 }
set_prove_orchestration off
set_engine_mode H
set_prove_per_property_time_limit 10m
prove -property {eq_cnt}
prove -with_helpers -property {<embedded>::test._assert_1}
puts "STATUS_EQ=[get_property_info -list status eq_cnt]"
puts "STATUS_ASSERT=[get_property_info -list status <embedded>::test._assert_1]"
puts "STATUS_PRE=[get_property_info -list status <embedded>::test._assert_1:precondition1]"
report -summary -result -force -file skill/proj_H_summary.rpt
```

Non-vacuity diagnostic run:

```bash
jg -fpv -batch -no_jges -proj skill/proj_cover_20260629_135314 -tcl skill/cover_precond.tcl
```

## Added Properties / Assumptions

- Added property `eq_cnt`:
  - `@(posedge clk) counter1 == counter2`
  - Status: `proven`
- Added helper activation:
  - `assert -set_helper eq_cnt`
  - Status: enabled after proving `eq_cnt`
- Added assumptions:
  - none
- Added bind checker:
  - none

## Final Status Counts

From [`skill/proj_H_summary.rpt`](/home/robin/Projects/awesome-formal-verification-skill/test/weak_model_ab/helper_counters/skill/proj_H_summary.rpt):

- Total properties: 4
- Assertions proven: 3
- Assertions cex: 0
- Assertions undetermined: 0
- Covers covered: 0
- Covers undetermined: 1

Per-property status in that run:

- `:noConflict` - proven
- `test._assert_1` - proven
- `test._assert_1:precondition1` - undetermined
- `eq_cnt` - proven

## Raw-RTL Status

- This is **not** an unqualified raw-RTL proof.
- The embedded assertion proof depends on the additional helper lemma `eq_cnt`, even though that helper was itself proven on the raw RTL.
- Because `test._assert_1:precondition1` stayed `undetermined`, I could not formally certify non-vacuity.

## Log Paths

- Final proof log: [`skill/proj_H_20260629_135202.log`](/home/robin/Projects/awesome-formal-verification-skill/test/weak_model_ab/helper_counters/skill/proj_H_20260629_135202.log)
- Final summary: [`skill/proj_H_summary.rpt`](/home/robin/Projects/awesome-formal-verification-skill/test/weak_model_ab/helper_counters/skill/proj_H_summary.rpt)
- Non-vacuity attempt log: [`skill/cover_precond_20260629_135314.log`](/home/robin/Projects/awesome-formal-verification-skill/test/weak_model_ab/helper_counters/skill/cover_precond_20260629_135314.log)
- Helper proof log: [`skill/eq_helper_20260629_134744.log`](/home/robin/Projects/awesome-formal-verification-skill/test/weak_model_ab/helper_counters/skill/eq_helper_20260629_134744.log)

## Timing

- Wall-clock from Jasper start to the first full proof of the embedded assertion: `7 s` (run started at `13:52:02` CST; summary printed at `13:52:09` CST).
- The proof phase itself was sub-second once the helper lemma was in place; the rest was analysis/elaboration/setup.
