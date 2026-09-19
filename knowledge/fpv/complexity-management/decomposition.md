# Complexity: Proof Decomposition

> Leaf of `complexity-management.md`. Break one hard proof into smaller obligations: assume-guarantee / compositional AG, helper lemmas, and state-space tunneling. Soundness rule: **only the propagated ROOT result is a verified signoff result** — local decomposition nodes are not.

## Proof Decomposition (AG / CAG)

**When to use**: Single property too complex; can be decomposed via helper lemmas or compositional reasoning.

## Helper vs. Proof Structure Decision

Use the lightest sound decomposition first, then escalate when signoff or scale
requires structure:

```
Direct proof stalls?
├─ Can one/few inductive invariants summarize
│  the missing local or global fact? ........ Yes → bounded helper trial
│    prove → gate on proven → select proven support → prove target
├─ Candidate CEX / undetermined? ............ Yes → do not trust as a theorem; classify feedback
│    reachable CEX → revise; missing support → capped SST/refinement below
├─ Helper graph has multiple stages? ........ Yes → proof_structure AG
├─ Helpers are as hard as the target? ....... Yes → proof_structure CAG/AG
├─ Many symmetric peer obligations with no
│  compact inductive summary? ................ Yes → proof_structure CAG
├─ Need auditable signoff? .................. Yes → proof_structure ROOT result
├─ Local helper proof could be mistaken
│  for top proof? ........................... Yes → proof_structure ROOT result
└─ Many peer properties / components? ....... Yes → CAG / partition
```

**Proven helpers are a proof method, not a modeling assumption**, when each
helper is proven from the same RTL and legal environment setup before theorem
reuse. Already-proven support is allowed; "independent" need not mean "alone". They
are ideal for local lemmas and for compact global summaries such as one
inductive uniqueness or conservation invariant whose proof converges in
isolation. The words `global`, `uniqueness`, `conservation`, or `peer` identify a
complexity risk; they do not by themselves require CAG.

### Compact Helper Trial

Use one bounded trial before building a proof structure when a small invariant
can summarize the missing fact:

```tcl
set matches [get_property_list -include {name *uniqueness_inv*}]
if {[llength $matches] != 1} {error "resolve one exact helper name first"}
set helper [lindex $matches 0]
prove -property $helper

if {[get_property_info $helper -list status] ne "proven"} {
  error "helper was not proven; do not reuse it as a theorem"
}

set_proven_directive true
prove -property [linsert $targets 0 $helper]
```

Keep the RTL, reset, and legal environment assumptions identical to the target
task. Do not add an assumption merely to make the helper prove. Report helper
and original-target status separately. If the trial fails, classify the result
using the refinement flow below; do not require failure or SST before accepting
a proven first candidate. Escalate instead of repeatedly extending the trial
when it requires many pairwise lemmas or reproduces the target's difficulty.

**Proof structure is a signoff framework** for multi-stage dependencies,
long-lived reviews, and decomposition experiments. It makes assume-side and
guarantee-side obligations explicit and gives a propagated ROOT result. Prefer
it when a benchmark or project asks for decomposition signoff, not just "target
eventually says proven".

**Do not confuse ProofMaster with proof structure.** ProofMaster is a cache and
strategy-reuse mechanism; it does not create assume-guarantee obligations or a
ROOT signoff node. If direct proof plus ProofMaster leaves most assertions
undetermined, change the proof shape instead of only extending time limits.

**CAG trigger pattern**: use `proof_structure -create
compositional_assume_guarantee` when a global invariant is distributed over many
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
# Use prove_with_support from "Helper Assertions" below; budgets are task inputs.
prove_with_support h_leaf {} $helper_budget
prove_with_support h_top {h_leaf} $helper_budget
prove_with_support target_prop {h_leaf h_top} $target_budget
```
Escalate this helper chain into `proof_structure` when there are multiple
helper layers or the report must prove the propagated ROOT node.

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
  lappend peer_props "top.gen[$i].local_invariant"
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

## Helper Assertions (Lemmas) [JG-specific]

**When to use**: Target property needs intermediate invariants to converge.
If supporting lemmas are proven but a higher-level lemma or target stalls,
check actual proof selection before changing its expression or extending time.

> 🔧 **VERSION-SENSITIVE — selection semantics validated on JasperGold
> 2025.12p002.** Check `help assert`, `help prove`, and
> `help set_proven_directive` on other releases.

Keep classification, proof evidence, and selected dependencies distinct:

| Atom / evidence | Meaning |
|---|---|
| `assert -helper -name h {<expr>}` / `assert -set_helper h` | Create a helper / convert a regular assertion to one. Neither proves it nor unconditionally assumes it. |
| Valid `status proven` under unchanged RTL/reset/environment | Discharged theorem; helper classification alone is not evidence. |
| `set_proven_directive true` + `prove -property {target h}` | Use selected already-proven `h` as support; ordinary assertions work too. |
| `prove -property target -with_helpers` | Include helper assertions; previously declared unproven helpers may also become proof obligations. |
| `prove -property target -with_proven` | Use all proven assertions in the same task; not an exact dependency whitelist. |

`set_proven_directive` defaults to `true`, but `prove -property target` alone
does **not** select every previously proven assertion. Merely marking a helper
is not an unsound assumption. The soundness boundary is trusting an unproved
fact as established, changing its setup, or leaving required obligations open.

**Explicit proven-support template**: use for a controlled sequential chain.
Resolve exact names in the same task; retain the same RTL, reset, assumptions,
and abstractions. Pass the support list to `prove`, not just to a Boolean test
that enables `-with_helpers`. Set budgets from the task; retain chosen engines.

```tcl
proc prove_with_support {target support limit} {
  foreach h $support {
    lassign [get_property_info $h -list {status validity_status}] status validity
    puts "SUPPORT_BEFORE $h $status $validity"
    if {$h eq $target || $status ne "proven" || $validity ne "proven"} {
      error "support $h is not a valid previously proven dependency"
    }
  }
  set selected [linsert $support 0 $target]
  puts "PROOF_SELECTED $selected"
  set_proven_directive true
  set result [prove -property $selected -per_property_time_limit_factor 0 \
    -per_property_time_limit $limit -time_limit $limit]
  lassign [get_property_info $target \
    -list {status validity_status min_length max_length}] status validity lo hi
  puts "PROOF_RESULT $target $result $status $validity $lo $hi"
  if {$status ne "proven" || $validity ne "proven"} {
    error "target $target not proven; stop this dependency chain"
  }
}

assert -name h_local {<local_invariant>}
assert -name h_summary {<higher_level_invariant>}
prove_with_support h_local {} $helper_budget
prove_with_support h_summary {h_local} $helper_budget
prove_with_support $target {h_local h_summary} $target_budget
```

Omit `-with_helpers` and `-with_proven` when the selected list must be exact.
Record the before-call statuses, selected names, `IPF036` pending/already-proven
counts, and final per-property status/validity/bounds. Distinguish newly proven
results from a later call that only reuses an already-proven result. Selection
does not establish that every support was necessary.

**Batch alternative**: `-with_helpers` may prove several unresolved helpers in
one call. This is not automatically circular reasoning or a false proof, but
do not describe it as sequential proof with only named prior dependencies.
Audit which obligations closed together and the original target's own result.
For helpers proven during a call, reuse by every engine is not guaranteed;
a subsequent explicit selection of the now-proven support can help.

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

## SST-Guided Helper Refinement [JG-specific]

> 🔧 **VERSION-SENSITIVE — validated on JasperGold 2025.12p002.** Recheck
> `help prove` and `help visualize` before standardizing this flow on another
> release.
>
> ⚠️ **NEEDS VALIDATION — command/trace semantics are tool-validated; a successful
> first candidate or an SST call alone does not validate refinement efficacy.**

**Trigger**: Use this diagnostic flow when an invariant-like assertion remains
`undetermined` after a sane direct proof, no reset-reachable CEX exists, and a
missing relation among state variables is plausible. Typical signals are a deep
antecedent, slowly growing BMC bound, or a target that looks true only because
of history not stated in the property. SST also helps bypass irrelevant
initialization prefixes. Do not use it as a generic response to every timeout;
first correct reset/setup errors and identify obvious cone-size causes.

### Choose the Entry Point

| Evidence available now | Next experiment |
|---|---|
| Clear compact candidate from RTL | Independently prove it with a capped budget; skip SST if it proves |
| No reasonable compact candidate | Diagnose the target with capped SST and inspect its state values |
| Candidate has a reset-reachable CEX in the unchanged model | Inspect that CEX; correct, weaken, or replace the false candidate |
| Candidate remains `undetermined`, missing support is plausible | Do not trust it as a theorem; check selection of any already-proven support, then use capped SST/refinement if needed |
| Candidate is as hard as the target or needs a large dependency graph | Escalate to AG/CAG instead of repeating diagnostics |

`undetermined` does not establish that a candidate is false. A true but
non-inductive candidate may need a stronger conjunction or separately proven
support, not weakening. If the model is abstracted, first classify whether a
candidate CEX is feasible in the original RTL. Never modify the environment
merely to exclude inconvenient states.

Jasper calls the result an **SST trace**. Do not rename it a design CEX or claim
that Jasper exposed an internal IC3/PDR counterexample to induction (CTI).
`prove -sst` runs without formal reset and without bounded assumptions while
requiring enabled helper/SST properties to hold for an initial prefix. If it
finds a violating continuation, the property remains `undetermined` and the
trace metadata carries `tag SST`. Jasper keeps reset behavior only as soft
constraints under `-prefer_quiet`; it is not a reachability proof.

`-sst N` sets the minimum SST trace length, not a reset-based BMC bound. Start
with `N=2` for a single-cycle state invariant (one predecessor plus one failing
state); choose a longer prefix for temporal properties. A trace may be longer
than `N`. If `N` is omitted, Jasper uses `set_sst_default_trace_length` (default
`15` in the validated release).

### Capture the Diagnostic State

Do not stop at the console message. Retrieve the stored SST trace and export its
signal values so an agent can reason from the actual states:

```tcl
set target <property_name>
set sst_n 2

set sst_result [prove -property $target -sst $sst_n -prefer_quiet \
  -engine_mode B -time_limit <diagnostic_budget>]
puts "SST_RETURN $sst_result"

lassign [get_property_info $target -list {status trace_id}] status trace_id
puts "SST_PROPERTY status=$status trace_id=$trace_id"

if {$trace_id ne ""} {
  set trace_info [get_trace_info $trace_id]
  puts "SST_TRACE $trace_info"
  array set trace_meta $trace_info
  if {![info exists trace_meta(tag)] || $trace_meta(tag) ne "SST"} {
    error "attached trace is not tagged SST; classify it before use"
  }

  visualize -violation -sst -property $target -trace_id $trace_id \
    -new_window sst_diag
  visualize -save -vcd [file normalize ./sst_diag.vcd] \
    -force -window sst_diag
}
```

An attached trace does not imply `status cex`. Record both fields. If no trace
is attached, inspect `sst_max_length`; a finite SST bound is not by itself a
full proof. Jasper can close a proof only when the normal reset-based
`min_length` and SST result overlap sufficiently.

### Read the Transition, Not Just the Failure

Use the available waveform reader to locate the last satisfying prefix state
and the failing state. Check returned sample times/counts and truncation; a
clock-edge query can omit the initial VCD state when the clock starts high.
Read that state explicitly by timestamp if missing. Do not treat one returned
sample as both states, or infer a relation from the helper pseudo-signal alone.
For temporal properties, retain the additional history required by the SVA.

When TraceWeave is available, use `get_formal_paths` for discovery and
`search_signals` to resolve paths. Use `get_signals_by_cycle` for edge-aligned
samples; use `get_signals_around_time` with `return_mode="values_only"`,
`window_ps=0`, and `extra_transitions=0` for missing timestamp samples. Convert
the waveform time unit to ps; select actual trace times, not assumed cycles.
An equivalent waveform reader is sufficient; TraceWeave is not a dependency.

For the changed state terms, inspect the RTL assignment that produced the next
value. Read its update enable, priority/select conditions, source operands,
and any validity or identity conditions, including signals absent from the
candidate expression. Compute the transition with the actual widths,
signedness, truncation, reset and SVA sampling semantics. A large arithmetic
sum alone does not establish failure of a modular bit-vector equality.

Explain which observed values take which update branch and break the candidate,
then propose a compact relation that excludes that impossible state family.
Check why reset could establish it and the RTL could preserve it; this is a
hypothesis to prove, not permission to constrain the environment. Prefer
range, phase/order, mutual-exclusion, correlation, and conservation relations
over helpers that restate the target or ban literal trace values.

### Refine, Prove, Then Reuse

Declare each candidate as an assertion and prove it from the same RTL,
clock, reset, and legal environment as the target. Do not add an assumption to
make the candidate pass.

Apply the entry-point decision to the actual candidate result. When diagnostic
feedback motivates a revision, record the old expression, the trace type and
state values, the newly proposed relation, and the new expression. Exclude an
impossible state family, not just the literal trace values. Prove each revision
from the unchanged setup; previously proven supporting lemmas may be used only
with their dependencies disclosed and without circular assumptions. Keep the
loop bounded and escalate to AG/CAG when the helper graph becomes multi-stage
or as hard as the target.

Before leaving this diagnostic route, record either the concrete revised
assertion/supporting lemma and its proof attempt, or why the evidence did not
support one (missing samples, unresolved update, uninformative trace, or budget
limit). Complete a bounded evidence-linked trial when a plausible relation is
available; do not substitute an engine change for that trial without a reason.
Do not invent a helper merely to satisfy a checklist. A syntax/printing fix,
unchanged candidate, tool call, or promise to refine is not a refinement result.
Keep success discovered directly from RTL distinct from trace-driven discovery.

For sequential theorem reuse, apply an explicit status gate and select support:

```tcl
assert -helper -name h_candidate {<candidate_invariant>}
prove -property h_candidate

set helper_status [get_property_info h_candidate -list status]
puts "HELPER_STATUS $helper_status"
if {$helper_status ne "proven"} {
  error "candidate is not independently proven; refusing theorem reuse"
}

set_proven_directive true
prove -property [list $target h_candidate]
```

Report any diagnostic trace separately from proof results. A sound completion records:

- target status before refinement (`undetermined`, bound, engine, time);
- when SST was used: property status, `trace_id`, trace length, and `tag SST`;
- every candidate result and its actual selected support;
- status gates before sequential reuse, or obligations closed together in a batch;
- final helper and target statuses, with `Infinite` bounds for full proof.

If the first candidate succeeds, report `refinement_not_exercised`; do not run
SST retrospectively to claim feedback caused its discovery. Distinguish
target-guided candidate discovery from revision of a failed candidate.

**Anti-patterns**:

- Requiring a deliberately wrong helper or mandatory SST before a clear first candidate.
- Counting diagnostic-tool use without an evidence-linked candidate revision as refinement.
- Calling an SST trace a reset-reachable bug or ordinary CEX.
- Saying “CTI” without disclosing that Jasper reported `tag SST`.
- Asking a model to infer a helper from `prove -sst` metadata without opening or
  exporting the trace.
- Reading only the failing state or the candidate's operands, without the
  predecessor and the RTL update's source/select conditions.
- Treating truncated clock-edge readback as a complete diagnostic transition.
- Explaining modular arithmetic using unbounded integer sums.
- Treating `assert -set_helper` as proof or as an unconditional assumption.
- Claiming an exact dependency list while the script only toggles `-with_helpers`.
- Replacing independent helper proof with `assume` or `assert -mark_proven`.

## See Also
- Shrinking the cone before decomposing (stopat/cutpoints/free vars): `cone-reduction.md`
- Index, soundness rules, anti-patterns: `../complexity-management.md`
