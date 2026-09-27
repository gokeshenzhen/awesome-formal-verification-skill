# FPV: End-to-End Workflow

> 🔬 **from-docs** — Generated from Cadence JasperGold documentation, 2026-06-14. Needs field validation. Content is [JG-specific]. ⚠️ Built from a single sample run-file — broad but shallow; many stages carry 📝 GAP.

## Overview

The chronological command sequence of a JasperGold FPV run: from `clear -all` through analyze, elaborate, clock/reset, constrain, declare properties, prove, and report. The command *order encodes dependencies* — getting it wrong (e.g., `clock` before `elaborate`, `prove` before constraints) breaks the run. Consult this module when setting up a new FPV environment or structuring a run file.

## Quick Decision Tree

Match the task scope before executing this flow: explain/review when asked to
analyze, author the requested properties/scripts when asked to write, and run
proof experiments within the authorized investigation. Consult
`complexity-management.md` → **Post-Baseline Triage** for feedback-driven routing.
Start with meaningful properties and add scope incrementally; proving a trivial
property does not establish the intended behavior. Distinguish exhaustive proof
from bounded or non-exhaustive search using the native result and proof scope.
For an authorized run, start the [Minimal Task Record](#minimal-task-record).
Use [Proof Acceptance](#proof-acceptance) and [Continue or Stop](#continue-or-stop)
when reporting results; a completed invocation alone does not close the task.

```
Setting up an FPV run?
└─ Follow the fixed stage order:
   clear → analyze → elaborate → inspect → clock/reset → constrain → properties
         → proof settings → sanity → (ProofMaster) → prove → review status
         → escalate proof shape if needed → report
   │
   ├─ Source language? .... -sv | -vhdl -lib L | -v2k -lib current | -verilog -f list
   ├─ Cut a sub-block? ..... elaborate ... -bbox_m {mods} / -bbox_i {insts}
   ├─ On a cluster? ........ set_proofgrid_mode / _shell / _per_engine_max_jobs  (before prove)
   ├─ Repeat runs? ......... set_proofmaster on  (before prove)
   ├─ Prove scope? ......... prove -property {name}  |  prove -all (assertions and covers)
   └─ Any proof feedback? ... use Post-Prove Escalation Gate below; for unresolved
                              obligations apply complexity-management.md triage
```

## Core Rules

1. **Command order is mandatory, not stylistic.** The canonical order is: `clear -all` → analyze → elaborate → inspect → clock/reset → constrain → properties → proof settings → sanity → ProofMaster → prove → report. Each stage depends on the previous.
2. **Always begin with `clear -all`** to wipe stale session state.
3. **Analyze before elaborate; elaborate before any design query, clock, or reset** — there is no design to attach to otherwise.
4. **Constrain (`assume`/`stopat`) and declare properties (`assert`/`cover`) before `prove`.**
5. **Sanity-check before proving**: `sanity_check` (clock/reset), `visualize -reset` (reset phase), `check_assumptions` (assumption conflicts). Proving against a broken or over-constrained setup yields vacuous or false results.
6. **Black-box heavy sub-blocks at elaboration** (`-bbox_m`/`-bbox_i`) to keep the proof tractable.
7. **Configure ProofGrid before proving** when running on a cluster; enable **ProofMaster** for repeated runs on the same/evolving design.
8. **After direct prove, review status before reporting success.** If more than 10% of assertions or more than 20 assertions remain `undetermined` with no counterexample, treat this as a complexity/proof-shape problem.
9. **Do not use ProofMaster as proof decomposition.** ProofMaster reuses proof cache and strategies; it does not create AG/CAG obligations or a propagated `ROOT` signoff node.
10. **Escalate global peer invariants to a decomposition decision.** For no-duplicate, uniqueness, conservation, mutual exclusion, placement, token ownership, or many generated queue/FIFO/bank/tile/arbitration assertions, apply complexity triage, then `complexity-management/decomposition.md` → **Helper vs. Proof Structure Decision**. That leaf owns helper versus AG/CAG/partition selection; require propagated `ROOT` status for proof-structure signoff.
11. **A run file is a template** — fill `<placeholders>` with real design files/config and your proof strategy.

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
prove -property {cover_name}   ;# run an existing cover; not `cover -property`
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
| Prove | `prove -property {n}` / `prove -all` | execute assertions or covers; `cover -name` only declares a cover |
| Report | `report -file <f> -detailed\|-summary` | detailed vs summary output |

## Post-Prove Escalation Gate

Inspect the latest result after direct proof, each helper trial, and each target
retry. Apply [`complexity-management.md` → **Post-Baseline Triage**](complexity-management.md#post-baseline-triage-jg-specific)
before selecting another experiment; the following is a summary of that routing:

```
Latest obligation result?
├─ Evidence/model/trace identity unclear? → resolve it through complexity triage
├─ Original targets and required obligations validly closed? → report completion
├─ Only helper proven? ........ closure: select for next obligation; search: objective gate
├─ Genuine reachable CEX? ..... distinguish helper repair from original-target investigation
└─ Unresolved? ............... complexity triage for objective/setup/capacity/support
   ├─ Helper/missing relation/dependencies? → decomposition.md method decision
   └─ Search or engine experiment selected? → engine-tuning.md
```

For sequential helper reuse, treat every helper and the final target as an
obligation with its own selected support. Under the same setup, prove lower-level
lemmas, then select them when proving the next helper, not only the final target.
"Independent" does not mean "without already-proven support". Gate sequential
reuse on valid `proven` status. [JG-specific] `assert -set_helper` only classifies
the assertion; `set_proven_directive true` plus an explicit `prove -property`
list selects exact support. A small acyclic chain need not become AG/CAG.
Alternatively, `-with_helpers` may prove several helpers together; disclose the selected
set and closed obligations, not a fictitious sequential dependency order. See
`complexity-management/decomposition.md` → **Helper Assertions** for templates.
Report the original targets' own valid results under the stated legal model and
the required support or jointly closed obligations. Accept a directly proven
baseline without inventing refinement; a successful first helper advances the
proof and is marked `refinement_not_exercised`, not task completion by itself.
When a helper does not converge, return to triage and the decomposition decision;
neither a high proven fraction nor a helper timeout chooses the next method.
The 10% / 20-assertion thresholds flag broad complexity; they do not exempt a
single remaining invariant from triage. ProofMaster may help repeated runs but
does not replace feedback classification or AG/CAG.
If the decision selects proof structure, create `SETUP`, initialize `ROOT`, build
the AG/CAG or partition operation, and report propagated `ROOT`. Local node
results are intermediate evidence, not signoff. Preserve unresolved results;
diagnostics or bounded results alone do not establish full proof.

## Minimal Task Record

Keep a short record in ordinary task-local files for an authorized proof/search
investigation. Use the following as a checklist, not a required schema or filename.
Save fixed inputs once per version and reference them from each check; add only
applicable helper/diagnostic details from the corresponding leaves. Preserve raw
tool output separately from the agent's interpretation. Mark missing facts as
unknown, unconfigured budgets as unset, and inapplicable fields as not applicable.

Separate these identities; a property name or Git HEAD alone is insufficient:

- **Model and objective:** snapshot the effective RTL/include files and file lists,
  top, defines/parameters, clock/reset, environment assumptions, cutpoints and
  abstractions/contracts, and the original property expressions/bindings. Keep
  the complete original-target inventory, including targets absent from later reports.
- **Candidate:** retain the helper expression/source version and its support
  references. Keep discarded versions as history; do not overwrite their evidence.
- **Check and configuration:** identify the tool project/session and invocation,
  actual tool version, ordinary-proof/search/diagnostic mode, engine portfolio,
  limits, and requested selection. Snapshot what the tool consumes at launch.

A check is one proof/search/diagnostic invocation, including a failed invocation;
status queries and polling are readbacks, not extra proof attempts. One candidate
version can have several checks. Use the decomposition leaf's **Candidate and
Support Record** to distinguish a semantic revision from syntax or selection repair.

```text
Task (once per input version): objective/scope; model snapshot; original targets
Budget: source; scope/unit; allowance/deadline; consumed/remaining; actual enforcer
Before check: call/project/session; model/candidate/config refs; requested selection
After check — facts: execution state; actual selection; raw output/error and timings
  Per obligation: name/role; native status/validity/bounds; result source call/path
  Mark newly obtained versus reused results; attach trace identity if applicable
Decision — interpretation: evidence refs; outstanding obligations; next action/reason
  Update budget; if ending, record stop reason and final status of every original target
```

Write the before-check entry before dispatch, attach results when returned, and
record the next decision before acting. Keep execution state (running, completed,
timed out, error, interrupted) distinct from every property's native result. A
failed call may have valid partial results; no returned result means unknown,
not an invented native status. Read actual selection from tool evidence; if it
cannot be established, retain that uncertainty instead of copying the request.
For [JG-specific] results, preserve `status`, `validity_status`, `min_length` and
`max_length`, plus trace metadata when applicable. Refer to
[`decomposition.md`](complexity-management/decomposition.md#candidate-and-support-record)
for support evidence and
[`sst-refinement.md`](complexity-management/sst-refinement.md#diagnostic-and-refinement-evidence)
for diagnostic readback; omit those extensions when unused.

### Input Changes, Reuse, and Recovery

Use hashes to identify bytes, not to establish semantic equivalence or proof
validity. When RTL/setup/abstraction/targets change, retain old results as history
and recheck affected obligations and dependencies against the current model.
For a changed helper, recheck its result and dependent uses; do not relabel a proof
of the old expression as proof of the new one. Reuse only with matching scope and
tool validity evidence or a separately established sound transfer. Mere comments,
renaming, or engine/time changes do not by themselves invalidate a theorem; still
record the change and verify applicability. Missing validity evidence is unresolved.

Use distinct call artifacts and retain the originating model/candidate/config
references. Do not mistake an attached old trace, cached result, or a report from
another session for a newly obtained result. Before reuse, check its current
validity and provenance; disclose both its original call and the reuse call.

On cancellation/interruption, preserve completed evidence, the pending call,
process/job ownership, last known state and budget consumption. Record a cancellation
request separately from confirmed termination; use available process control only
for this task's owned jobs. On resume, reconcile any live owned call and partial
files before launching another; recheck actual inputs, tool context, result/trace
identity and validity, and remaining budget. A half-written report cannot establish
completion. Recover verified partial results without resetting the task budget;
if elapsed usage is unavailable, mark it unknown rather than assigning zero.
These are recovery checks, not a promise of automatic resume or process termination.

## Proof Acceptance

For safety proof closure, require each unchanged original target's valid full
proof under the stated legal model, with its actual support/joint obligations
closed. [JG-specific] Check the ordinary proof's native status, validity and
unbounded result (`Infinite` bounds); an isolated SST bound or an exit code of zero
does not establish this. A `covered` result answers its cover objective, not a
safety assertion; bounded or non-exhaustive results retain their stated scope.
Disclose abstractions and trusted contracts; a hash match does not prove that an
abstract-model result transfers to the original RTL.

Apply sequential support gates or audit the jointly closed set using the
decomposition leaf. For AG/CAG, require propagated `ROOT` in addition to the local
evidence; ordinary helper proof does not require a ROOT task. Record actual
selection without claiming it is the minimal necessary support set.

Accept a discarded candidate remaining Unknown only when it has left the final
proof obligation set and the accepted result does not depend on it. Preserve its
history. If the tool still lists it as a required open obligation, close it or
explicitly remove it and revalidate the final result/dependencies before acceptance.
Do not weaken the original target or legal environment to obtain success.

Report every original target separately, including proven, refuted, unprocessed
and unresolved targets. A helper CEX refutes that candidate; only a genuine reachable
CEX for an original target refutes that target in its legal model. Resolve unknown
model/trace identity before claiming refutation. Retain partial completion even
when another target is refuted or the investigation ends without full closure.

## Continue or Stop

Classify available feedback through complexity triage before deciding; apply the
following task-level limits before launching its selected next experiment. Require
new evidence, a justified relation/support change, or an independent configuration
experiment with a concrete purpose. An unchanged replay may answer a reproducibility
question; renaming a run, increasing helper count, or rewording the same guess is
not evidence of progress. A single timeout ends that attempt, not automatically
the investigation. Continue only when the proposed action fits the authorized scope
and available budget; reserve time for diagnosis, revised proof and final reporting.

Record each configured budget's source (user/project/host), unit, scope, allowance,
consumed/remaining amount and actual enforcer. Do not invent universal retry counts
or time limits. Distinguish the following accounting scopes:

| Scope | Accounting and enforcement boundary |
|---|---|
| Single solve/property | Retain native time and configured solver limits; [JG-specific] `-time_limit` and per-property limits do not cap all startup/export work |
| One EDA invocation wall time | Measure launch to completion/termination, including setup/export; a hard cap requires an actual process/job controller covering that interval |
| Cumulative EDA calls | Sum the declared per-call metric, including failed/retried calls; specify whether wall or CPU time and how parallel calls are counted |
| Whole investigation/session | Include agent analysis, readback and waiting; disclose active-time versus elapsed-time accounting across pauses and the enforcing host/controller, if any |

Parallel call-time sums differ from elapsed wall time. Carry cumulative usage
across renamed scripts, new projects and resumed sessions. If no budget is supplied,
record unset and stay within authorized work; unset is not unlimited authorization.
Without an actual enforcer for a scope, describe its limit as cooperative/soft.
Knowledge instructions alone cannot guarantee a deadline or kill a running job.
When a configured total budget is exhausted, do not launch more work under it;
record overrun if any, rather than claiming the limit was enforced.

| Ending | Required conclusion and evidence |
|---|---|
| Success | Apply Proof Acceptance; for a search/cover task report only its requested objective and witness scope |
| Original target refuted | Identify the target, model and genuine reachable CEX; preserve other targets' results and investigate intent within scope |
| Total budget exhausted | Report incomplete with unresolved obligations and budget accounting; retain valid partial proofs |
| No justified next action | Report incomplete, list open obligations and the concrete blocker or why no evidence-based action fits; do not require exhausting every technique |
| Tool/input blocked | Retain raw error or missing input and existing results; do not classify an execution error as a design CEX |
| User stop or pause | Record the request, pending work and recovery information; preserve existing proof statuses |

An SST, candidate CEX, missing trace or Unknown is feedback to classify, not by
itself a task ending. Budget/no-next-action/tool/user endings do not establish
mathematical unprovability. Keep task completion, individual property results,
and refinement evidence separate; a first-candidate success needs no forced revision.

## Anti-Pattern Reference

| Anti-Pattern | Why It Fails | Correct Alternative |
|-------------|-------------|-------------------|
| Skipping `clear -all` | Stale session state contaminates the run | Start every run file with `clear -all` |
| `clock`/`reset` before `elaborate` | No elaborated design to attach to | analyze → elaborate first |
| `prove` before `assume`/`assert`/`cover` | Nothing constrained or declared | Constrain + declare properties first |
| Proving without sanity/assumption checks | Broken or over-constrained setup → vacuous/false results | Run `sanity_check` + `visualize -reset` + `check_assumptions` first |
| Proving a huge design with no black-boxing/stopat | State-space explosion | Black-box (`-bbox_*`) or `stopat` heavy sub-blocks at setup |
| Re-running direct `prove -all` after many `undetermined` results | Same proof shape keeps hitting capacity | Apply complexity triage and the decomposition method decision before another run |
| Treating helper classification as proven evidence | An undetermined helper can be mistaken for a valid lemma | Gate sequential theorem reuse on valid `proven` status; verify actual selection |
| Treating ProofMaster as AG/CAG | Cache reuse does not decompose obligations | Use `proof_structure` and check propagated `ROOT` |
| Calling a zero exit code, missing trace or isolated diagnostic bound a proof | Execution and diagnostic facts do not discharge the original obligations | Apply Proof Acceptance to native results and actual dependencies |
| Reusing a result by property name after input changes | The report may belong to another model or candidate | Retain input identities and recheck applicability/validity |
| Treating a solver timeout as a hard session deadline | Startup, readback and agent work have different scopes | Record each budget's scope, source and actual enforcer |

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

> 📝 GAP — Beyond the task record and acceptance rules above, the single sample run-file does not cover project directory structure, interactive (GUI) vs batch invocation, full CEX debug methodology, CI/CD integration, or a complete production signoff policy. Validate actual agent behavior and project-specific signoff separately.

## Further Reading
- For the Tcl language and scripting idioms behind these commands: see `tcl-commands.md`
- For property/`assert`/`cover` authoring: see `property-writing.md`
- For engine/proof settings and bounds signoff: see `engine-tuning.md`
- For complexity reduction (`stopat`, black-boxing, abstraction): see `complexity-management.md`
