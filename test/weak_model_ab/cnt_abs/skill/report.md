# JasperGold FPV Report

## Result

- Design: `cnt_abstract_eg`
- Outcome: full proof achieved on the RTL with a sound counter abstraction on `cntr`
- Assertions: 7 proven, 0 cex, 0 undetermined, 0 errors
- Covers: 6 covered, 0 unreachable, 0 undetermined, 0 errors
- Task count: 1

## Properties Written

- `A_set`: if `cntr == 32'd8369262`, then `A` is high on the next sampled cycle.
- `B_set`: if `cntr == 32'd268407145`, then `B` is high on the next sampled cycle.
- `A_sticky`: once `A` is high, it remains high until reset.
- `B_sticky`: once `B` is high, it remains high until reset.
- `C_low`: `C` is always low outside reset.
- `D_low`: `D` is always low outside reset.
- `reach_A`: cover the exact counter milestone that triggers `A`.
- `reach_B`: cover the exact counter milestone that triggers `B`.

## Knowledge Used

- `knowledge/fpv/property-writing.md`: provided the clocked SVA patterns, `assert property` / `cover property` usage, and the reset-disabling style.
- `knowledge/fpv/workflow.md`: provided the JasperGold run order (`clear` → `analyze` → `elaborate` → `clock/reset` → `sanity_check` → `check_assumptions` → `prove` → `report`).
- `knowledge/fpv/complexity-management.md`: pointed to abstraction for deep counters.
- `knowledge/fpv/complexity-management/abstraction.md`: supplied the decisive tactic, `abstract -counter cntr -values 0 8369262 268407145`, which made the deep milestone reachability covers tractable.
- Own reasoning: derived the exact target constants from the RTL comparisons, mapped the one-shot/sticky semantics of `A` and `B`, and concluded `C` and `D` remain low because the RTL never assigns them after reset.

## Exact JasperGold Commands

### Batch invocation

```bash
jg -fpv -batch -proj skill/proj_20260629_144002 -tcl skill/run_jg.tcl
```

### Tcl script executed

```tcl
clear -all
analyze -sv cnt_abstract_eg.sv skill/cnt_abstract_eg_checker.sv
elaborate -top cnt_abstract_eg
clock clk
reset ~rst_n
abstract -counter cntr -values 0 8369262 268407145
sanity_check
check_assumptions
prove -all
report -summary -result -force -file skill/final_report.rpt
```

## Abstraction / Assumptions

- No environment assumptions were added.
- This is not an unqualified raw-RTL proof in the strictest sense because the non-vacuity witnesses rely on JasperGold counter abstraction for `cntr`.
- The safety assertions are still sound under that abstraction.
- The cover witnesses are abstraction-aided witnesses for the exact trigger milestones; they are not brute-force raw-cycle witnesses.

## Runtime

- Wall-clock time from batch start to first full proof: `10.784 s`

## Logs

- Batch console log: [skill/proj_20260629_144002/console.log](/home/robin/Projects/awesome-formal-verification-skill/test/weak_model_ab/cnt_abs/skill/proj_20260629_144002/console.log)
- Jasper console log: [skill/proj_20260629_144002/jg_console.log](/home/robin/Projects/awesome-formal-verification-skill/test/weak_model_ab/cnt_abs/skill/proj_20260629_144002/jg_console.log)
- Session log: [skill/proj_20260629_144002/sessionLogs/session_0/jg_session_0.log](/home/robin/Projects/awesome-formal-verification-skill/test/weak_model_ab/cnt_abs/skill/proj_20260629_144002/sessionLogs/session_0/jg_session_0.log)
- Jasper summary report: [skill/final_report.rpt](/home/robin/Projects/awesome-formal-verification-skill/test/weak_model_ab/cnt_abs/skill/final_report.rpt)
