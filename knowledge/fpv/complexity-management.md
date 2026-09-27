# Complexity Management for Formal Property Verification

> **Mature** — Generated from Cadence JasperGold documentation, 2026-03-29. Organized as an **index + sub-topic leaves** (progressive disclosure): this file is the map (decision tree, rules, anti-patterns, command reference); the detailed pattern bodies live in `complexity-management/*.md`. Read this first, then drill into the relevant leaf.

## Overview

Complexity management is the core discipline that determines whether formal proofs converge or time out. It covers abstraction (counter, memory, initial-value, synchronizer), cone-cutting with `stopat`/cutpoints, free-variable/NDC methods, proof decomposition (AG, CAG, helpers), profiler-guided workflows, targeted simplification knobs, and under/over-constraint management. Consult this module whenever a property is bounded or inconclusive after reasonable engine time.

## Quick Decision Tree

### Post-Baseline Triage [JG-specific]

Use this section for outcome, objective, and capacity triage;
[`complexity-management/decomposition.md`](complexity-management/decomposition.md#helper-vs-proof-structure-decision)
owns helper/structural/AG-CAG method selection, and
[`complexity-management/sst-refinement.md`](complexity-management/sst-refinement.md#choose-the-entry-point)
owns diagnostic capture, readback, and revision. Reapply triage after each result,
including before preparing a final script. A new filename or unchanged expression
is not new evidence. Record the selected route and the latest evidence for it.

Keep the requested scope: explanation/review tasks need analysis, and authoring
tasks need the requested properties/scripts and appropriate checks; neither
automatically starts a proof campaign. For an authorized investigation, apply
the following gates **in order**, returning here after each new result:

1. **Identify the evidence.** Match the obligation (original target or helper),
   current model, native status/validity, and trace type. Resolve missing results,
   tool errors, or uncertain model/trace identity before choosing a proof method.
   In an abstracted or suspect setup, establish original-RTL feasibility before
   calling a trace a genuine reset-reachable CEX. An SST is diagnostic only.
2. **Accept valid success.** If the original targets and required obligations
   are closed, use `workflow.md` → **Post-Prove Escalation Gate** to report them.
   If only a helper proved in a proof-closure task, select it for the next
   obligation using **Helper Assertions** in the decomposition leaf; do not
   equate it with target success. For a pending search objective, retain that
   helper result and continue to the objective gate. A successful first candidate
   needs no retrospective SST; report `refinement_not_exercised` for that candidate.
3. **Handle a genuine CEX before support repair.** For a helper, use the
   decomposition leaf's **Candidate-CEX Repair** branch. For an original target,
   report that target refuted in its legal model and investigate RTL/property/
   environment intent. Proven support cannot remove a legal execution that
   falsifies the candidate. Do not turn a helper CEX alone into a design-bug lead.
4. **Honor the search objective.** For explicit bug-search/reachability or a
   concrete witness lead for the original objective, use `engine-tuning.md` →
   **DBH Escalation Boundary**. Do not impose helper closure on a search task.
   "Strongest sound conclusion" or a finite budget alone does not select DBH.
5. **Triage setup/capacity for unresolved proof closure.** For `undetermined`
   with no genuine CEX, correct reset/setup errors and handle obvious capacity
   symptoms using the map below before selecting a missing-relation diagnostic.
   A large memory/counter cause takes priority over a speculative state relation.
6. **Repair omitted support for this unresolved obligation.** Check valid proven
   support and its actual `prove` selection using **Helper Assertions**. Correct
   an omission and retry; support selected only for the final target cannot help
   an earlier helper. If already selected, continue rather than repeat that run.
7. **Choose the proof method from the remaining evidence.** For an invariant-like
   target/helper whose state may be related by reset and subsequent updates,
   a plausible missing state relation is enough to read **Helper vs. Proof
   Structure Decision** in the decomposition leaf; a finished helper is not
   required. That decision gives structural trials and justified AG/CAG priority
   over generic SST, permits a clear first candidate, and diagnoses missing or
   stalled candidates when appropriate. Use the other symptom routes below or
   evidence-based engine selection when this proof shape does not apply.

### Symptom Routes After Triage

Use this map within the gates above, not as a competing priority order. In
particular, resolve setup/obvious capacity before the missing-relation route.

```
Property not converging?
├─ X-state / reset issues? .... Yes → abstraction.md "Initial Value Abstraction (IVA)"
├─ Large counters in cone? .... Yes → abstraction.md "Counter Abstraction"
├─ Large memories in cone? .... Yes → abstraction.md "Memory Abstraction"
├─ Raw mem proof stalled? ..... Yes → abstraction.md "Memory Abstraction" trigger checklist
│     (big array flops + arbitrary-address assertion + precond cover hits + no CEX → abstract, don't re-race engines)
├─ Synchronizers in path? ..... Yes → abstraction.md "Synchronizer Abstraction"
├─ Config logic dominates? .... Yes → cone-reduction.md "Configuration Cutpoints with Legality Assumptions"
├─ Multi-instance / symmetric?  Yes → cone-reduction.md "Free Variables / NDC"
├─ Many irrelevant signals? ... Yes → cone-reduction.md "Profiler-Guided Stopat Mining"
├─ Design too large overall? .. Yes → cone-reduction.md "Parameter Reduction"
├─ Invariant undetermined, no reset CEX, missing state relation plausible?
│                              Yes → decomposition.md "Helper vs. Proof Structure Decision"
├─ Have you profiled? ......... No → formal_profiler → cone-reduction.md "Profiler-Guided Stopat Mining"
├─ Many peer/global invariants? Yes → decomposition.md "Helper vs. Proof Structure Decision"
├─ Single property too hard? .. Yes → decomposition.md "Helper vs. Proof Structure Decision"
├─ Need lemma scaffolding? .... Yes → decomposition.md "Helper Assertions"
├─ Stuck before interesting states?
│                              Yes → decomposition.md diagnostic eligibility → sst-refinement.md
├─ One property far harder? ... Yes → targeted-reductions.md "Per-Property Simplification"
├─ Multi-clock robustness? .... Yes → targeted-reductions.md "Clock Ratio Management"
└─ False CEX / missed bugs? ... Yes → "Under/Over-Constraint Management" (below)
```

## Sub-Topic Index

| Leaf | Techniques |
|---|---|
| [`complexity-management/abstraction.md`](complexity-management/abstraction.md) | Counter abstraction (auto + manual 4-step), Initial Value Abstraction (IVA), Memory abstraction, Synchronizer abstraction |
| [`complexity-management/cone-reduction.md`](complexity-management/cone-reduction.md) | Free variables / NDC, **Configuration cutpoints + legality assumptions** (`stopat`, `setup_ndc`), Profiler-guided stopat mining, Parameter reduction |
| [`complexity-management/decomposition.md`](complexity-management/decomposition.md) | Proof decomposition (AG / CAG / multi-stage), helper assertions, data correspondence |
| [`complexity-management/sst-refinement.md`](complexity-management/sst-refinement.md) | Candidate-result branching, SST capture/readback, helper refinement and proof gates |
| [`complexity-management/targeted-reductions.md`](complexity-management/targeted-reductions.md) | **Per-property simplification** (`set_per_property_simplification`), Clock ratio management |

## Core Rules

1. **Profile before abstracting.** Use `formal_profiler` to identify zero-effort signals; blind abstraction risks cutting proof-relevant state.
2. **Always pair `abstract -init_value` with `assume -bound 1`.** Freeing initial state without re-constraining legal invariants causes spurious counterexamples.
3. **Use explicit `-values` for signoff.** `abstract -counter -find` is exploratory; commit to explicit milestone values in production scripts.
4. **Include reset value `0` in counter abstraction values.** Omitting it breaks the reset-to-milestone path.
5. **`stopat`/cutpoints alone are never sufficient.** Always add legality assumptions (`assume -constant`, `assume -bound 1`, `setup_ndc`, or transition constraints) after cutting a signal.
6. **Separate helper classification from proven support.** [JG-specific] `assert -set_helper` marks an assertion as a helper; it neither proves it nor unconditionally assumes it. Gate sequential theorem reuse on a valid `proven` result under the same setup, and explicitly select the intended support. Batch helper proof is also valid; report which obligations it actually closes.
7. **Classify SST traces before interpreting them.** A JasperGold SST trace is an arbitrary-state diagnostic witness, not a reset-reachable CEX or an exposed IC3/PDR CTI; the target remains `undetermined`. Retrieve its `trace_id`, confirm `tag SST`, inspect/export the waveform, and use it only to propose candidate invariants.
8. **Choose helpers by proof shape, not by property label.** Follow the decomposition leaf's method decision after triage. Try compact local or global invariants, including small acyclic chains with proven support; use `proof_structure` for justified dependency/scale/signoff needs. A timeout alone does not choose AG/CAG or SST.
9. **Separate model setup from proof decomposition.** Create a `SETUP` task first, then derive `ROOT` from it.
10. **For `proof_structure`, sign off ROOT, not just local AG/CAG nodes.** Require the propagated ROOT status; this does not require a ROOT task for ordinary helper proofs.
11. **Detect overconstraint actively.** Use `check_assumptions -dead_end` and reachability covers to ensure assumptions don't block real behavior.
12. **Persist reductions to files.** Write generated `stopat` decks to `.tcl` files via `eju_list_to_file` so they survive across sessions.

## Anti-Pattern Reference

| Anti-Pattern | Why It Fails | Correct Alternative |
|---|---|---|
| `reset -none` | X-state explosion, spurious CEX | `reset rst` with correct polarity |
| `abstract -counter -find` in signoff | Exploratory; may miss thresholds | `abstract -counter sig -values 0 v1 v2` |
| `stopat` / cutpoint without re-constraining | Signal fully unconstrained → unrealistic traces | `assume -constant` + legality bounds; `setup_ndc` |
| Cutpoint config signals without legality | Proof explores impossible/invalid configurations | Pair config cutpoints with validity-check assumptions |
| `abstract -init_value` without `assume -bound 1` | Explores impossible initial states | Always pair with `assume -bound 1` |
| Treating `assert -set_helper` as proof or an unconditional `assume` | Confuses a helper label with discharged evidence | Check valid proof status before theorem reuse; inspect actual proof selection |
| `prove -property target` after proving helpers, expecting automatic reuse | Proven helpers outside the selected set are not automatically used | `set_proven_directive true` + explicit target/support list, or a disclosed broader selection |
| Reporting an SST trace as a design CEX / CTI | SST omits formal reset and leaves the target `undetermined` | Confirm `tag SST`; report it only as a diagnostic witness |
| Running `prove -sst` without reading its trace | The agent sees metadata, not the missing state relation | Query `trace_id`, open the trace, and export/read its waveform |
| Requiring SST before trying a clear compact helper | Adds work without establishing a missing fact | Independently prove the candidate first; diagnose only when needed |
| Selecting DBH solely from "strongest conclusion" or a finite budget | Skips diagnosis of a plausible missing state relation | Apply post-baseline triage before ordinary deepening or Hunt |
| Routing a helper-repair task to DBH just because its candidate has a CEX | Confuses a false candidate with a design-bug lead | Inspect the failed obligation; use the candidate-CEX repair branch |
| CAG local node result as signoff | Not sound | Use propagated ROOT result only |
| Overconstraints on baseline task | Masks real bugs | Clone: `task -create oc -source_task baseline -copy_all` |
| Proving all IDs simultaneously | State explosion | One stable symbolic `chosen_id` |
| `-bbox_i` without abstract reconnect | Outputs unconstrained | Add `assume` tying outputs |
| Rewriting the DUT module, reporting as raw signoff | Proves the replacement, not the design | `-bbox_i <path>` + reconnect; disclose contract as trusted abstraction |
| Re-racing engines on a stalled arbitrary-address memory assertion | State explosion never converges | Apply memory-abstraction trigger checklist (`abstraction.md`) |
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
| `assert -set_helper <name>` | Convert a regular assertion to a helper assertion; no proof implied | JG |
| `set_proven_directive true` + `prove -property {target h}` | Reuse selected already-proven `h`; gate its status first | JG |
| `prove -property <p> -with_helpers` | Include helper assertions, potentially including unproven obligations | JG |
| `prove -property <p> -with_proven` | Include all proven assertions in the same task as assumptions | JG |
| `prove -property <p> -sst <N>` | State space tunneling | JG |
| `set_sst_default_trace_length <N>` | Default SST minimum trace length when `-sst` omits `N` | JG |
| `get_property_info <p> -list {status trace_id}` | Distinguish property status from attached SST trace | JG |
| `get_trace_info <trace_id>` | Inspect trace length and `tag SST` metadata | JG |
| `visualize -violation -sst -property <p> -trace_id <id> -new_window <w>` | Open a selected SST trace in SST mode | JG |
| `visualize -save -vcd <file> -force -window <w>` | Export the trace for signal-level analysis | JG |
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
