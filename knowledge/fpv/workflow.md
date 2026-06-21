# FPV: End-to-End Workflow

> 🔬 **from-docs** — Generated from Cadence JasperGold documentation, 2026-06-14. Needs field validation. Content is [JG-specific]. ⚠️ Built from a single sample run-file — broad but shallow; many stages carry 📝 GAP.

## Overview

The chronological command sequence of a JasperGold FPV run: from `clear -all` through analyze, elaborate, clock/reset, constrain, declare properties, prove, and report. The command *order encodes dependencies* — getting it wrong (e.g., `clock` before `elaborate`, `prove` before constraints) breaks the run. Consult this module when setting up a new FPV environment or structuring a run file.

## Quick Decision Tree

```
Setting up an FPV run?
└─ Follow the fixed stage order:
   clear → analyze → elaborate → inspect → clock/reset → constrain → properties
         → proof settings → sanity → (ProofMaster) → prove → report
   │
   ├─ Source language? .... -sv | -vhdl -lib L | -v2k -lib current | -verilog -f list
   ├─ Cut a sub-block? ..... elaborate ... -bbox_m {mods} / -bbox_i {insts}
   ├─ On a cluster? ........ set_proofgrid_mode / _shell / _per_engine_max_jobs  (before prove)
   ├─ Repeat runs? ......... set_proofmaster on  (before prove)
   └─ Prove scope? ......... prove -property {name}  |  prove -all
```

## Core Rules

1. **Command order is mandatory, not stylistic.** The canonical order is: `clear -all` → analyze → elaborate → inspect → clock/reset → constrain → properties → proof settings → sanity → ProofMaster → prove → report. Each stage depends on the previous.
2. **Always begin with `clear -all`** to wipe stale session state.
3. **Analyze before elaborate; elaborate before any design query, clock, or reset** — there is no design to attach to otherwise.
4. **Constrain (`assume`/`stopat`) and declare properties (`assert`/`cover`) before `prove`.**
5. **Sanity-check before proving**: `sanity_check` (clock/reset), `visualize -reset` (reset phase), `check_assumptions` (assumption conflicts). Proving against a broken or over-constrained setup yields vacuous or false results.
6. **Black-box heavy sub-blocks at elaboration** (`-bbox_m`/`-bbox_i`) to keep the proof tractable.
7. **Configure ProofGrid before proving** when running on a cluster; enable **ProofMaster** for repeated runs on the same/evolving design.
8. **A run file is a template** — fill `<placeholders>` with real design files/config and your proof strategy.

## The Canonical FPV Run File

```tcl
clear -all

## 1. ANALYZE  (choose per source language)
analyze -vhdl -lib <library_name> <Vhdl_files>
analyze -sv <SystemVerilog_files>
analyze -v2k -lib current <Verilog_files>
analyze -verilog -f <file_list>

## 2. ELABORATE  (optionally black-box modules/instances)
elaborate -top <top_mod_name> -bbox_m {module_list} -bbox_i {instance_list}

## 3. INSPECT design
get_design_info
get_design_info -list <bbox_inst|input|flop|register>

## 4. CLOCK & RESET
clock <clock_name>
reset <type> <reset_name>

## 5. CONSTRAIN
assume -env -name <name> <expression>
stopat <expression>

## 6. PROPERTIES
assert -name <name> <expression>
cover  -name <name> <expression>

## 7. PROOF SETTINGS  (cluster)
set_proofgrid_mode <option>
set_proofgrid_shell <full_path_to_shell_plus_args>
set_proofgrid_per_engine_max_jobs <N>

## 8. SANITY  (clock / reset / assumptions)
sanity_check
visualize -reset
check_assumptions

## 9. ProofMaster  (optional; accelerates repeat runs)
set_proofmaster on
set_proofmaster_dir <path>
set_proofmaster_max_data_age <N>

## 10. PROVE
prove -property {property_name}
prove -all

## 11. REPORT
report -file <file_name> -detailed   ;# or -summary
```

## Stage Notes & Decision Guidance

| Stage | Command(s) | Choose |
|---|---|---|
| Analyze | `analyze` | `-sv` (SystemVerilog), `-vhdl -lib L` (VHDL), `-v2k -lib current` (Verilog-2001), `-verilog -f list` (Verilog-95 file list) |
| Elaborate | `elaborate -top` | add `-bbox_m {mods}` / `-bbox_i {insts}` to black-box complex sub-blocks |
| Inspect | `get_design_info -list ...` | `bbox_inst` / `input` / `flop` / `register` |
| Clock/Reset | `clock`, `reset` | set both before constraining |
| Constrain | `assume -env`, `stopat` | `stopat` cuts a driver to reduce complexity |
| Properties | `assert`, `cover` | property bodies are SVA — see `property-writing.md` |
| Proof settings | `set_proofgrid_*` | only needed for cluster runs |
| Sanity | `sanity_check`, `visualize -reset`, `check_assumptions` | always run before `prove` |
| ProofMaster | `set_proofmaster on` | for repeated runs on the same/evolving design |
| Prove | `prove -property {n}` / `prove -all` | one property vs everything |
| Report | `report -file <f> -detailed\|-summary` | detailed vs summary output |

## Anti-Pattern Reference

| Anti-Pattern | Why It Fails | Correct Alternative |
|-------------|-------------|-------------------|
| Skipping `clear -all` | Stale session state contaminates the run | Start every run file with `clear -all` |
| `clock`/`reset` before `elaborate` | No elaborated design to attach to | analyze → elaborate first |
| `prove` before `assume`/`assert`/`cover` | Nothing constrained or declared | Constrain + declare properties first |
| Proving without sanity/assumption checks | Broken or over-constrained setup → vacuous/false results | Run `sanity_check` + `visualize -reset` + `check_assumptions` first |
| Proving a huge design with no black-boxing/stopat | State-space explosion | Black-box (`-bbox_*`) or `stopat` heavy sub-blocks at setup |

## Tool-Specific Notes

### JasperGold
- The run-file stage order above is the standard JasperGold FPV App methodology.
- `sanity_check`, `visualize -reset`, and `check_assumptions` are the standard pre-prove sanity trio.
- `set_proofmaster on` enables cross-run proof reuse (see `engine-tuning.md`).

### VC Formal
> 📝 GAP — No VC Formal workflow content in the current sources. To be added.

## Command Reference
| Command | Purpose | Tool |
|---|---|---|
| `clear -all` | reset session state | JG |
| `analyze -vhdl\|-sv\|-v2k\|-verilog [-lib L] [-f list] <files>` | read source by language | JG |
| `elaborate -top <m> [-bbox_m {..}] [-bbox_i {..}]` | elaborate; optional black-boxing | JG |
| `get_design_info [-list bbox_inst\|input\|flop\|register]` | design summary / details | JG |
| `clock <name>` / `reset <type> <name>` | define clock / reset | JG |
| `assume -env -name <n> <expr>` | environment constraint | JG |
| `stopat <expr>` | cut a driver at a point (complexity) | JG |
| `assert -name <n> <expr>` / `cover -name <n> <expr>` | declare property / cover | JG |
| `set_proofgrid_mode\|_shell\|_per_engine_max_jobs` | cluster proof settings | JG |
| `sanity_check` | verify clock/reset setup | JG |
| `visualize -reset` | debug/analyze the reset phase | JG |
| `check_assumptions` | detect assumption conflicts | JG |
| `set_proofmaster on` / `_dir <p>` / `_max_data_age <N>` | enable & configure ProofMaster | JG |
| `prove -property {name}` / `prove -all` | prove one / all properties | JG |
| `report -file <f> -detailed\|-summary` | write a results report | JG |

> 📝 GAP — The single sample run-file does not cover: project directory structure, interactive (GUI) vs batch invocation, CEX/counterexample debug workflow, the iterative refinement cycle (analyze failures → tighten constraints → re-prove), CI/CD integration, and formal signoff criteria. Add user-guide/methodology sources to fill these.

## Further Reading
- For the Tcl language and scripting idioms behind these commands: see `tcl-commands.md`
- For property/`assert`/`cover` authoring: see `property-writing.md`
- For engine/proof settings and bounds signoff: see `engine-tuning.md`
- For complexity reduction (`stopat`, black-boxing, abstraction): see `complexity-management.md`
