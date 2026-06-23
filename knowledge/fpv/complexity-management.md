# Complexity Management for Formal Property Verification

> **Mature** — Generated from Cadence JasperGold documentation, 2026-03-29. Organized as an **index + sub-topic leaves** (progressive disclosure): this file is the map (decision tree, rules, anti-patterns, command reference); the detailed pattern bodies live in `complexity-management/*.md`. Read this first, then drill into the relevant leaf.

## Overview

Complexity management is the core discipline that determines whether formal proofs converge or time out. It covers abstraction (counter, memory, initial-value, synchronizer), cone-cutting with `stopat`/cutpoints, free-variable/NDC methods, proof decomposition (AG, CAG, helpers), profiler-guided workflows, targeted simplification knobs, and under/over-constraint management. Consult this module whenever a property is bounded or inconclusive after reasonable engine time.

## Quick Decision Tree

```
Property not converging?
├─ Have you profiled? ......... No → formal_profiler → cone-reduction.md "Profiler-Guided Stopat Mining"
├─ Large counters in cone? .... Yes → abstraction.md "Counter Abstraction"
├─ Large memories in cone? .... Yes → abstraction.md "Memory Abstraction"
├─ X-state / reset issues? .... Yes → abstraction.md "Initial Value Abstraction (IVA)"
├─ Synchronizers in path? ..... Yes → abstraction.md "Synchronizer Abstraction"
├─ Config logic dominates? .... Yes → cone-reduction.md "Configuration Cutpoints with Legality Assumptions"
├─ Multi-instance / symmetric?  Yes → cone-reduction.md "Free Variables / NDC"
├─ Many irrelevant signals? ... Yes → cone-reduction.md "Profiler-Guided Stopat Mining"
├─ Design too large overall? .. Yes → cone-reduction.md "Parameter Reduction"
├─ Single property too hard? .. Yes → decomposition.md "Proof Decomposition (AG/CAG)"
├─ Need lemma scaffolding? .... Yes → decomposition.md "Helper Assertions"
├─ Stuck in init cycles? ...... Yes → decomposition.md "State Space Tunneling (SST)"
├─ One property far harder? ... Yes → targeted-reductions.md "Per-Property Simplification"
├─ Multi-clock robustness? .... Yes → targeted-reductions.md "Clock Ratio Management"
└─ False CEX / missed bugs? ... Yes → "Under/Over-Constraint Management" (below)
```

## Sub-Topic Index

| Leaf | Techniques |
|---|---|
| [`complexity-management/abstraction.md`](complexity-management/abstraction.md) | Counter abstraction (auto + manual 4-step), Initial Value Abstraction (IVA), Memory abstraction, Synchronizer abstraction |
| [`complexity-management/cone-reduction.md`](complexity-management/cone-reduction.md) | Free variables / NDC, **Configuration cutpoints + legality assumptions** (`stopat`, `setup_ndc`), Profiler-guided stopat mining, Parameter reduction |
| [`complexity-management/decomposition.md`](complexity-management/decomposition.md) | Proof decomposition (AG / CAG / multi-stage), Helper assertions (lemmas), State space tunneling (SST) |
| [`complexity-management/targeted-reductions.md`](complexity-management/targeted-reductions.md) | **Per-property simplification** (`set_per_property_simplification`), Clock ratio management |

## Core Rules

1. **Profile before abstracting.** Use `formal_profiler` to identify zero-effort signals; blind abstraction risks cutting proof-relevant state.
2. **Always pair `abstract -init_value` with `assume -bound 1`.** Freeing initial state without re-constraining legal invariants causes spurious counterexamples.
3. **Use explicit `-values` for signoff.** `abstract -counter -find` is exploratory; commit to explicit milestone values in production scripts.
4. **Include reset value `0` in counter abstraction values.** Omitting it breaks the reset-to-milestone path.
5. **`stopat`/cutpoints alone are never sufficient.** Always add legality assumptions (`assume -constant`, `assume -bound 1`, `setup_ndc`, or transition constraints) after cutting a signal.
6. **Prove helpers before using them.** `assert -set_helper` on an unproven assertion is unsound; always `prove -property helper` first.
7. **Separate model setup from proof decomposition.** Create a `SETUP` task first, then derive `ROOT` from it.
8. **Sound results live on ROOT, not on local AG/CAG nodes.** Only the propagated ROOT status is the verified result.
9. **Detect overconstraint actively.** Use `check_assumptions -dead_end` and reachability covers to ensure assumptions don't block real behavior.
10. **Persist reductions to files.** Write generated `stopat` decks to `.tcl` files via `eju_list_to_file` so they survive across sessions.

## Anti-Pattern Reference

| Anti-Pattern | Why It Fails | Correct Alternative |
|---|---|---|
| `reset -none` | X-state explosion, spurious CEX | `reset rst` with correct polarity |
| `abstract -counter -find` in signoff | Exploratory; may miss thresholds | `abstract -counter sig -values 0 v1 v2` |
| `stopat` / cutpoint without re-constraining | Signal fully unconstrained → unrealistic traces | `assume -constant` + legality bounds; `setup_ndc` |
| Cutpoint config signals without legality | Proof explores impossible/invalid configurations | Pair config cutpoints with validity-check assumptions |
| `abstract -init_value` without `assume -bound 1` | Explores impossible initial states | Always pair with `assume -bound 1` |
| Unproven helper as `-set_helper` | Unsound lemma | `prove -property helper` first |
| CAG local node result as signoff | Not sound | Use propagated ROOT result only |
| Overconstraints on baseline task | Masks real bugs | Clone: `task -create oc -source_task baseline -copy_all` |
| Proving all IDs simultaneously | State explosion | One stable symbolic `chosen_id` |
| `-bbox_i` without abstract reconnect | Outputs unconstrained | Add `assume` tying outputs |
| Wide clock ranges by default | Exponential complexity | Fixed-factor first; ranges last |
| Profiling without isolating property | Misleading effort scores | `assert -disable *; assert -enable <target>` |

## Under/Over-Constraint Management

### Underconstraint (false alarms)
- **Symptom**: CEX shows behavior impossible in real design
- **Fix**: `reset -non_resettable_regs 0`; add `assume -reset`; apply IVA pattern (`abstraction.md`)
- **Diagnosis**: Add history witness signals to track impossible state sequences in CEX

### Overconstraint (missed bugs)
- **Symptom**: Properties pass but covers are unreachable
- **Detection**: `check_assumptions -dead_end [-minimize]`
- **Practice**: Clone tasks for experiments:
```tcl
task -create oc_test -source_task baseline -copy_all -set
assume -name oc_constraint {<expr>}
```
- **Recovery**: `get_needed_assumptions -property <prop> -engine_mode {B4 I N}`

> 📝 GAP: No extraction covers automated regression-level overconstraint detection across property suites.

## Tool-Specific Notes

### JasperGold
- `complexity_manager [-property <prop>]`: auto-selects abstractions; locates counters, FIFOs, arrays, arithmetic blocks, and candidate cutpoints. Manual override if thresholds missed.
- `formal_profiler`: mine zero-effort signals for safe `stopat` candidates
- `get_design_info -list fsm|counter|array -no_aggregate -silent`: enumerate design structures
- `visualize -relevant_logic <prop> -configuration undriven_only`: inspect proof cone
- `proof_structure`: AG, CAG, partition, hard_case_split decomposition
- `set_proofmaster on; set_proofmaster_dir <dir>`: persist proof cache across sessions
- `hunt -config -mode cycle_swarm|state_swarm`: advanced cover/proof search
- `set_engineL_overconstraining_factor 0.3`: tune engine-L aggressiveness
- `set_prove_clock_optimization on`: reduce multi-clock scheduling overhead
> 🔧 VERSION-SENSITIVE: CAG and `proof_structure` commands documented for JG 2021.06FCS and 2023.03FCS. Syntax may differ in earlier versions.

### VC Formal
> 📝 GAP: No source extractions cover VC Formal complexity management. To be added.

## Command Reference

| Command | Purpose | Tool |
|---|---|---|
| `abstract -counter <sig> -values <v0> <v1>` | Milestone counter abstraction | JG |
| `abstract -counter -find` | Discovery pass for abstractable counters | JG |
| `abstract -init_value <sig>` | Free initial value of signal | JG |
| `abstract -reset_value <sig>` | Free reset value of signal | JG |
| `stopat <signal>` | Cut signal from proof cone (cutpoint) | JG |
| `stopat -remove <signal>` | Restore previously cut signal | JG |
| `stopat -env <signal>` | Cut env-side cone | JG |
| `setup_ndc <sig> -legal {<expr>}` | Cut signal as legally-constrained non-det choice | JG |
| `assume -bound 1 {<cond>}` | Constrain initial state only | JG |
| `assume -constant <sig>` | Make signal time-invariant (spatial NDC) | JG |
| `complexity_manager -property <prop>` | Auto-select abstractions / find cutpoints | JG |
| `formal_profiler -show <p> -list bound` | List profiled bounds | JG |
| `formal_profiler -report -bound $c -signal $s` | Signal effort at bound | JG |
| `get_design_info -list fsm\|counter\|array` | Enumerate design structures | JG |
| `elaborate -bbox_i <inst>` | Black-box specific instance | JG |
| `elaborate -bbox_m <module>` | Black-box all instances of module | JG |
| `elaborate -parameter <name> <value>` | Override design parameter | JG |
| `proof_structure -init ROOT` | Initialize proof tree | JG |
| `proof_structure -create assume_guarantee` | AG decomposition | JG |
| `proof_structure -create compositional_assume_guarantee` | CAG decomposition | JG |
| `proof_structure -create partition` | Partition properties | JG |
| `assert -helper -name <n> {<expr>}` | Declare helper lemma | JG |
| `assert -set_helper <name>` | Activate proven helper | JG |
| `prove -property <p> -with_helpers` | Use helpers in proof | JG |
| `prove -property <p> -sst <N>` | State space tunneling | JG |
| `set_per_property_simplification on\|off` | Precondition-based per-property simplification | JG |
| `check_assumptions -dead_end` | Detect overconstraint | JG |
| `get_needed_assumptions -property <prop>` | Find minimal assumption set | JG |
| `reset -non_resettable_regs 0` | Suppress non-resettable warnings | JG |
| `set_word_level_reduction on` | Enable word-level reasoning | JG |
| `set_prove_advanced_simplification on` | Advanced simplification | JG |
| `set_prove_clock_optimization on` | Multi-clock optimization | JG |
| `set_engine_threads <N>` | Parallel engine threads | JG |

## Further Reading

- Detailed technique bodies: `complexity-management/{abstraction,cone-reduction,decomposition,targeted-reductions}.md`
- For engine selection and tuning strategies: see `engine-tuning.md`
- For SVA property writing patterns: see `property-writing.md`
- For Tcl scripting of these commands: see `tcl-commands.md`
