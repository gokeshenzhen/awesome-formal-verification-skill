# Complexity: Proof Decomposition

> Leaf of `complexity-management.md`. Break one hard proof into smaller obligations: helper lemmas, assume-guarantee / compositional AG, and state-space tunneling. When using `proof_structure`, require the propagated ROOT result for signoff, not just local node results.

## Helper vs. Proof Structure Decision

Apply [`../complexity-management.md` → **Post-Baseline Triage**](../complexity-management.md#post-baseline-triage-jg-specific)
first if the latest evidence has not been classified. It handles scope, completed
results, original-target CEX, search objectives, setup/capacity, and omitted
support. For proof closure, a valid first helper goes to **Helper Assertions**
for reuse; a genuine helper CEX goes to **Candidate-CEX Repair** below.
Neither needs an SST trial.

This section owns method selection for the **remaining unresolved proof**.
With no genuine CEX, a sound setup, no overriding capacity issue, and the intended
valid support selected, apply the **first matching** method below. Reapply the
outcome triage after each trial; do not classify every new expression as a first
candidate. A mere timeout is not evidence of a large dependency graph.
If the latest feedback is an SST attempt, finish its readback or no-information
branch in `sst-refinement.md` before choosing another run.

| Priority / evidence | Next action |
|---|---|
| Explicit assume/guarantee or ROOT signoff required; dependency graph hard to audit; many peer obligations with no compact summary; or supported strengthening remains as hard as the target after feedback analysis with no useful compact next relation | Use **Proof Decomposition (AG / CAG)**: AG for staged dependencies, CAG for distributed peer relations, or partition. Require propagated `ROOT`; SST is not a prerequisite |
| Diagnostic unavailable/uninformative, with no new candidate, support, or evidence justifying renewed diagnosis | Choose a bounded non-diagnostic alternative with a concrete reason, or report unresolved if none fits the budget; do not repeat the same diagnostic solely because status is still Unknown |
| Local selected-entry/output-data equality is `undetermined`; proven count/index/control support is selected; RTL exposes a compact structural strengthening not yet tried | Use one capped **Data-Correspondence Strengthening** trial before generic SST |
| That structural candidate remains `undetermined` and missing state support is plausible | Diagnose that candidate with capped SST and read its transition before another split/join formulation |
| No failed candidate yet and one/few compact local or global invariants summarize the missing fact | Prove the first candidate with selected support and a capped budget; advance if validly proven |
| Invariant-like obligation has a plausible missing state relation and either no reasonable compact candidate or another candidate still `undetermined` despite selected support | Diagnose the target (no candidate) or stalled candidate with capped SST; read the actual states before revising |
| None of the above has evidence | Use the index's profiling/reduction routes or a justified engine experiment; identify the missing evidence instead of forcing SST or AG/CAG |

**Proven helpers are a proof method, not a modeling assumption**, when each
helper is proven from the same RTL and legal environment setup before theorem
reuse. **Independent does not mean alone**: use already-proven lemmas to prove
another helper, then use that helper to prove the final target. A small acyclic
chain does not require AG/CAG merely because it has several levels. The words
`global`, `uniqueness`, `conservation`, or `peer` identify a complexity risk;
they do not by themselves require CAG.

### Candidate-CEX Repair

Use this branch only after confirming that the violated obligation is the
candidate and the trace is reset-reachable in the same legal model. Read the
actual predecessor/failing states and RTL update guards and sources; use
`sst-refinement.md` → **Read the Transition, Not Just the Failure** for the
readback discipline, without issuing SST for this CEX. Correct, weaken, or
replace the false relation, then prove the revision with its selected valid
support. Do not constrain away legal behavior. A helper CEX refutes that helper,
not automatically the original target; adding an omitted true theorem cannot
repair it. If feasibility is uncertain due to abstraction/setup, return to
evidence classification instead of weakening the candidate blindly.

## Helper Assertions (Lemmas) [JG-specific]

**When to use**: Prove or reuse a helper selected by the method decision above.
For an unresolved obligation not refuted by a genuine CEX, correct omitted valid
support first. If it still stalls with that support selected, reapply the method
decision; a proven sibling does not discharge this unresolved relation.

> 🔧 **VERSION-SENSITIVE — selection semantics validated on JasperGold
> 2025.12p002.** Check `help assert`, `help prove`, and
> `help set_proven_directive` on other releases.

### Sequential Proven Support

Treat each helper and the final target as an **obligation with its own support
list**. Selecting local lemmas only for the final target does not help an earlier
helper proof. Use the same procedure at every level; pass `{}` only when no
previously proven support is selected for that obligation.

Resolve exact names in the same task and keep RTL, clock/reset, assumptions,
and abstractions unchanged. Use the caller's engine settings and task budgets.
Pass the support list to `prove`, not just to a Boolean test for `-with_helpers`:

```tcl
proc prove_with_support {obligation support limit engines} {
  if {![llength $engines]} {error "pass the recorded ordinary-proof engine portfolio"}
  foreach h $support {
    lassign [get_property_info $h -list {status validity_status}] status validity
    puts "SUPPORT_BEFORE $h $status $validity"
    if {$h eq $obligation || $status ne "proven" || $validity ne "proven"} {
      error "support $h is not a valid previously proven dependency"
    }
  }
  set selected [linsert $support 0 $obligation]
  puts "PROOF_SELECTED $selected"
  set_proven_directive true
  set result [prove -property $selected -engine_mode $engines -per_property_time_limit_factor 0 \
    -per_property_time_limit $limit -time_limit $limit]
  lassign [get_property_info $obligation \
    -list {status validity_status min_length max_length}] status validity lo hi
  puts "PROOF_RESULT $obligation $result $status $validity $lo $hi"
  if {$status ne "proven" || $validity ne "proven"} {
    error "obligation $obligation not proven; stop this dependency chain"
  }
  return $result
}

assert -name h_local {<local_invariant>}
assert -name h_summary {<higher_level_invariant>}
set support_of(h_local) {}
set support_of(h_summary) {h_local}
set support_of($target) {h_local h_summary}
# Set ordinary_engines from the recorded ordinary trial, not the SST engine.
prove_with_support h_local $support_of(h_local) $helper_budget $ordinary_engines
prove_with_support h_summary $support_of(h_summary) $helper_budget $ordinary_engines
prove_with_support $target $support_of($target) $target_budget $ordinary_engines
```

**Fresh-session trigger:** before a diagnostic or final script recreates these
helpers, copy the dependency map, definitions, setup and ordinary engine/limit
record together. Rebuild dependencies in order with the same calls above; select
each helper's own dependencies while proving it. A loop that proves every helper
alone loses the chain even if all names appear later in the diagnostic list.
Check current-session status **and** validity after each call. Stop a dependent
call when its support is unresolved; an old project's theorem is not current
proof state. If the remaining budget cannot rebuild the chain, report that limit
instead of silently shortening the proof or diagnosing without intended support.
For SST, select the stalled obligation with its rebuilt support; reserve Engine B
for the diagnostic call. Log deliberate engine/limit changes as separate trials.

An inconclusive result stops sequential theorem reuse along that chain, not all
further investigation. Classify the result using the triage and method decision
above; do not require failure or SST before accepting a proven first candidate.
Do not add an assumption merely to make a helper pass.

**Branch before spending the next budget.** Do not queue an unconditional long
target retry immediately after a trial helper. If the helper is still
`undetermined`, `-with_proven` gains no new theorem from it. Record its result,
check support selection, then use the method decision above. When it selects
diagnosis, read `sst-refinement.md` and reserve a capped diagnostic and
revised-helper proof before another unchanged target attempt. Keep the structural
trial and dependency/scale branches available; record the evidence for the choice.

Before launching a trial, allocate separate time for that trial, possible
diagnosis, revised obligations, and the final target, including tool startup.
Do not let a speculative candidate plus a prequeued target retry consume the
entire recovery budget. Keep scripts/expressions from each attempt; syntax
repairs are not semantic helper revisions.

Record a `HELPER_DECISION` before the next run: obligation, status/validity,
selected proven support, next action and its evidence, remaining budget, and
time reserved for diagnosis/revision and final proof. For an `undetermined`
candidate, apply the method priority above; when it selects missing-relation
diagnosis, do that before an unchanged retry unless new proof evidence justifies
the retry. After a target retry with newly proven partial support also stalls,
reclassify the remaining relations using the same decision. Repeating the same
expressions and support with a shorter limit does not validate closure; reserve such a replay for a
concrete reproducibility question. Retain the current script for delivery and
spend the investigation budget on new evidence. If stopping early, identify
the concrete blocker or explain why no
useful investigation fits; merely reporting the same timeout is not that reason.

For the first feedback-driven retry, preserve the stalled obligation's ordinary
engine portfolio and limit while changing its relation/support. Judge engine
changes separately; a good control-lemma engine is not necessarily a good
payload engine. See `sst-refinement.md` → **Refine, Prove, Then Reuse**.

### Candidate and Support Record

Extend [`../workflow.md` → **Minimal Task Record**](../workflow.md#minimal-task-record)
for helper work; reference shared model, call, configuration and budget entries
instead of duplicating them. Use `HELPER_DECISION` for the interpretation/next-action
part, with the native evidence linked separately:

```text
Candidate: obligation name; expression/source version; originating check
Support: requested and actual selection; each result's model/version/source
  Sequential: before-call status/validity; joint: member set and closure results
Change: before/after expression and support refs; meaning changed; evidence/reason
HELPER_DECISION: latest result refs; selected route; next action and evidence
  Remaining budget and diagnosis/revision/final reserves: reference task record
```

Version every candidate edit; count a semantic revision only when the intended
relation or supporting facts change. Syntax fixes, renaming, equivalent split/join
forms and engine-only retries are not semantic revisions. Distinguish adding a
newly justified supporting relation from repairing selection of already-intended
support. Label discovery, revision, selection repair, syntax repair and replay
according to what happened; a changed file hash alone does not decide the label.

For sequential reuse, require valid proof in the same legal model and evidence
that support was actually selected. An unselected theorem can remain valid but
does not establish its use in this call. For joint proof, retain the actual member
set and each closed/open result; never convert pending members into assumed facts.
If all required members close together, accept that joint result without inventing
a sequential order. Report final target status separately and apply workflow's
**Proof Acceptance**, including its discarded-candidate and propagated ROOT gates.

For an existing assertion, resolve its exact name before using the same template:

```tcl
set matches [get_property_list -include {name *uniqueness_inv*}]
if {[llength $matches] != 1} {error "resolve one exact helper name first"}
set helper [lindex $matches 0]
prove_with_support $helper $support $helper_budget $ordinary_engines
```

### Classification, Evidence, and Selection

| Atom / evidence | Meaning |
|---|---|
| `assert -helper -name h {<expr>}` / `assert -set_helper h` | Create a helper / convert a regular assertion to one. Neither proves it nor unconditionally assumes it. |
| Valid `status proven` under unchanged RTL/reset/environment | Discharged theorem; helper classification alone is not evidence. |
| `set_proven_directive true` + `prove -property {obligation h}` | Use selected already-proven `h` for a helper or final target; ordinary assertions work too. |
| `prove -property target -with_helpers` | Include helper assertions; previously declared unproven helpers may also become proof obligations. |
| `prove -property target -with_proven` | Use all proven assertions in the same task; not an exact dependency whitelist. |

`set_proven_directive` defaults to `true`, but `prove -property obligation` alone
does **not** select every previously proven assertion. Merely marking a helper
is not an unsound assumption. The soundness boundary is trusting an unproved
fact as established, changing its setup, or leaving required obligations open.

Omit `-with_helpers` and `-with_proven` when the selected list must be exact.
Record before-call statuses, selected names, `IPF036` pending/already-proven
counts, and final per-property status/validity/bounds. Distinguish newly proven
results from later calls that only reuse a result. Selection does not establish
that every support was necessary. Report the original target's own result.

### Tool-Managed Batch Alternative

`-with_helpers` may prove several unresolved helpers in one call. This is also a
valid proof strategy, not automatically circular reasoning or a false proof.
Audit which obligations closed together; do not describe the batch as sequential
proof with only named prior dependencies. For helpers proven during a call,
reuse by every engine is not guaranteed; a subsequent explicit selection of the
now-proven support can help.

**Example** (batch proof with loop-generated FIFO tag helpers):
```tcl
for {set i 0} {$i < 16} {incr i} {
  assert -helper -name help_tag_$i \
    "(id_fifo.fifo_valid\[$i\] && id_fifo.fifo_out\[$i\]\[0\]) |-> \
     (id_fifo.fifo_out\[$i\]\[75:68\] == v_top.ID)"
}
prove -property {top.v_top.ast_has_same_id_on_ID} -time_limit 2m -with_helpers
```

**Gotchas**:
- `-with_helpers` is one selection method, not a requirement for explicit-list reuse.
- `assert -mark_proven helper`: injects externally verified result (soundness depends on external proof)
- Loop-generated helpers must escape `[` and `]` in Tcl strings
- If helper dependencies become hard to audit, move the same obligations into
  `proof_structure` and require the propagated ROOT result.

## Data-Correspondence Strengthening

Use this pattern when the method decision above selects a structural trial,
after setup/capacity and support checks. When a selected-entry or output-data
equality remains hard after its control relations prove and are selected,
inspect what supplies that data on the **next** transition.
A head-only fact does not constrain the next stored entry when a pointer moves.
After a capped local trial, reserve a bounded structural trial before spending
the remaining budget on the unchanged helper or target. SST can inform this
trial; it is not a prerequisite when RTL already exposes the missing source.
If this structural candidate also stays undetermined with its intended support
selected and no reachable CEX, reapply the method decision. Unless evidence now
requires the dependency/scale branch, diagnose missing state support with capped
SST before alternating between more split and joined formulations. A new expression does not restart
the first-candidate branch. Preserve the candidate and read its failing
transition, then decide which relation or support to change. If diagnostics
are unavailable or uninformative, record that result and choose a bounded
alternative from evidence; reserve time for the revised proof and final target.

Derive the live-data correspondence from the RTL: validity/ownership, logical
position, and payload equality. Within the bounded structural trial, **follow
load sources**, not only storage indices:

- Substitute each covered location's RTL next-state assignment into its proposed
  equality, alongside the reference-model update. Check hold, load, move and
  invalidation branches under their actual guards.
- If a load takes its payload from another stored value or registered handoff,
  add that source's guarded data correspondence and inspect its updates too.
  Continue until sources are covered, share the same legal input/reference update,
  or have valid proven support; prove mutually preserving clauses together.
- Enumerating every slot of one array or proving its count/index facts does not
  establish the payload of a later write into that array. A source left with only
  control facts still needs a data relation or an explicit reason none is needed.

Guard stale/unoccupied locations by validity; do not equate unused storage or
forbid a legal transfer merely to remove a counterexample. Use the trace to locate
the gap and reset/update rules to generalize beyond the observed values. This is
a candidate-construction method, not a substitute for proving the result.

Prove range, count and pointer/wrap consistency separately where convenient,
then select that valid support for the payload obligation. Payload clauses may
preserve one another as data moves between locations: try a **single conjunction**
or a tool-managed joint proof instead of requiring every clause to prove alone.
Discharge the whole conjunction before reuse; never assume the other unproven
clauses. For small fixed storage, explicit live-position clauses are a reasonable
trial; for large storage, use a justified symbolic representative, abstraction or
AG/CAG rather than unbounded enumeration. Keep the original target unchanged.

**Arithmetic model check [JG-specific]**: inspect analysis/proof warnings after
adding index expressions. On JG 2025.12p002, a non-power-of-two `%` expression in
a Tcl assertion can emit `WNL033` and be automatically blackboxed; the resulting
CEX is not automatically feasible in the original model. Where a proven range
gives `0 <= sum < 2*N`, sized conditional subtraction
`sum >= N ? sum - N : sum` implements one wrap without that operator. Keep enough
bits for the sum and prove the range; do not apply this rewrite outside it.

## Proof Decomposition (AG / CAG)

**Proof structure is a signoff framework** for multi-stage dependencies,
long-lived reviews, and decomposition experiments. It makes assume-side and
guarantee-side obligations explicit and gives a propagated ROOT result. Prefer
it when a benchmark or project asks for decomposition signoff, not just "target
eventually says proven".

**Do not confuse ProofMaster with proof structure.** ProofMaster is a cache and
strategy-reuse mechanism; it does not create assume-guarantee obligations or a
ROOT signoff node. If direct proof plus ProofMaster leaves most assertions
undetermined, change the proof shape instead of only extending time limits.

**CAG trigger pattern**: after the method decision selects decomposition, use
`proof_structure -create compositional_assume_guarantee` when a global invariant is distributed over many
symmetric peers and no compact helper converges, such as pairwise uniqueness,
mutual exclusion, or no-duplicate properties across many queues, FIFOs,
arbiters, banks, or tiles. CAG is also preferred when the helper graph itself is
the peer dependency graph or signoff requires explicit assume/guarantee
obligations. Build a CAG property set from the peer invariants and prove the
propagated ROOT result. Do not choose CAG solely because the property is named
uniqueness or conservation.

**Arithmetic datapath pattern**: for compressor trees, reductions, encoders, and
other word-level datapaths, first look for local algebraic identities:
```tcl
assert -name h_leaf {leaf.sum_in == leaf.sum_out}
assert -name h_top {top_sum == rtl_sum}
# Use prove_with_support from "Helper Assertions" above; budgets are task inputs.
prove_with_support h_leaf {} $helper_budget $ordinary_engines
prove_with_support h_top {h_leaf} $helper_budget $ordinary_engines
prove_with_support target_prop {h_leaf h_top} $target_budget $ordinary_engines
```
Escalate this helper chain into `proof_structure` under the method decision's
dependency/scale/signoff conditions, not solely because one trial timed out.

**Template** (Assume-Guarantee):
```tcl
task -create SETUP -copy_assert -set
# Build helpers (e.g., virtual_net + assert)
proof_structure -init ROOT -from SETUP -copy_all
proof_structure -create assume_guarantee \
  -from ROOT -op_name AG1 -imp_name {AG1.G AG1.A} \
  -property [list helper1 target_prop]
prove -property AG1.A::target_prop    ;# prove target assuming helper
prove -property AG1.G::helper1        ;# prove helper independently
```

**Template** (Compositional Assume-Guarantee):
```tcl
proof_structure -init ROOT -from SETUP \
  -copy_assumes -copy_abstractions all -copy_stopats
proof_structure -create compositional_assume_guarantee \
  -from ROOT -op_name CAG -property [list prop1 prop2 ...]
prove -task {CAG.0} -assert -engine {N} -time_limit 100s
prove -task {CAG.1} -assert -engine {N} -time_limit 100s
# Check ROOT status — that is the sound result
```

**Template** (CAG for generated peer invariants):
```tcl
set peer_props {}
for {set i 0} {$i < $N} {incr i} {
  lappend peer_props [format {top.gen[%d].local_invariant} $i]
}
proof_structure -init ROOT -from SETUP -copy_all
proof_structure -create compositional_assume_guarantee \
  -from ROOT -op_name CAG_peers -property $peer_props
prove -task {CAG_peers.0} -assert -engine {N AM H} -time_limit 10m
::jasper::psu::prove_all ROOT
report
```

**Template** (Multi-Stage AG for scaling):
```tcl
set ML_helpers_2:5 "helper2 helper3 helper4 helper5"
set ML_helpers_1:5 "helper1 ${ML_helpers_2:5}"
proof_structure -init ROOT -from SETUP -copy_all
# Stage 1: prove helpers 2:5
proof_structure -create assume_guarantee -from ROOT \
  -op_name AG_stage1 -property [list ${ML_helpers_2:5}]
# Stage 2: use helpers 1:5 to prove target
proof_structure -create assume_guarantee -from ROOT \
  -op_name AG_stage2 -property [list ${ML_helpers_1:5} addN.target]
```

**Runtime data** (adderN benchmark):
| N | Direct proof | With AG decomposition |
|---|---|---|
| 8 | ~1 min | — |
| 12 | ~50 min | ~90 s |
| 16 | ~3.6 h | ~11 min |

**Gotchas**:
- CAG supports embedded SVA only (no bind-style assertions)
- `-copy_abstractions all` is required — env constraints must propagate to CAG nodes
- `::jasper::psu::prove_all ROOT` auto-proves all obligations in the proof tree
- Local CAG node results are NOT sound; only propagated ROOT is valid for signoff

## SST-Guided Helper Refinement [JG-specific]

When the method decision selects diagnosis, read [`sst-refinement.md`](sst-refinement.md)
for SST capture, waveform inspection, evidence-linked revision, and normal-proof
gates. That leaf does not override the first structural trial or justified AG/CAG
choice. A candidate CEX uses **Candidate-CEX Repair** above. A successful first
candidate needs no retrospective SST; report `refinement_not_exercised`.

## Anti-Patterns

- Repairing selection instead of analyzing a genuine candidate CEX.
- Letting generic Unknown-to-SST routing override the first structural trial.
- Treating every timeout as a mandatory AG/CAG escalation, or requiring SST when
  explicit dependency/scale/signoff evidence already selects proof structure.
- Trusting helper classification or local AG/CAG node results as target signoff.

## See Also
- Shrinking the cone before decomposing (stopat/cutpoints/free vars): `cone-reduction.md`
- Index, soundness rules, anti-patterns: `../complexity-management.md`
