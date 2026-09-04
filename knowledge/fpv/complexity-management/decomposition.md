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
│    prove alone → gate on proven → assert -set_helper → prove -with_helpers
├─ Helper independently proven from the
│  same setup, without new assumptions? ..... No  → do not set helper; use AG/CAG
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
helper is proven from the same RTL and legal environment setup before use. They
are ideal for local lemmas and for compact global summaries such as one
inductive uniqueness or conservation invariant whose proof converges in
isolation. The words `global`, `uniqueness`, `conservation`, or `peer` identify a
complexity risk; they do not by themselves require CAG.

### Compact Helper Trial

Use one bounded trial before building a proof structure when a small invariant
can summarize the missing fact:

```tcl
set helper [lindex [get_property_list -include {name *uniqueness_inv*}] 0]
assert -disable *
assert -enable $helper
prove -property $helper

if {[llength [get_property_list \
        -include {name *uniqueness_inv* status proven}]] != 1} {
  error "helper was not proven; do not activate it"
}

assert -set_helper $helper
assert -enable *
prove -property $targets -with_helpers
```

Keep the RTL, reset, and legal environment assumptions identical to the target
task. Do not add an assumption merely to make the helper prove. Report helper
and original-target status separately. Escalate instead of extending the helper
trial when the candidate remains undetermined, requires many pairwise lemmas,
or reproduces the original target cone and difficulty.

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
assert -helper -name h_leaf {leaf.sum_in == leaf.sum_out}
prove -property h_leaf
assert -set_helper h_leaf
assert -helper -name h_top {top_sum == rtl_sum}
prove -property h_top -with_helpers
prove -property target_prop -with_helpers
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

## Helper Assertions (Lemmas)

**When to use**: Target property needs intermediate invariants to converge.

**Template**:
```tcl
assert -helper -name helper1 {<invariant_expression>}
prove -property helper1
assert -set_helper helper1
prove -property target_prop -with_helpers
```

**Multi-stage helper template**:
```tcl
assert -helper -name h1 {<local invariant>}
prove -property h1
assert -set_helper h1

assert -helper -name h2 {<higher-level invariant>}
prove -property h2 -with_helpers
assert -set_helper h2

prove -property target_prop -with_helpers
```

**Example** (loop-generated FIFO tag helpers):
```tcl
for {set i 0} {$i < 16} {incr i} {
  assert -helper -name help_tag_$i \
    "(id_fifo.fifo_valid\[$i\] && id_fifo.fifo_out\[$i\]\[0\]) |-> \
     (id_fifo.fifo_out\[$i\]\[75:68\] == v_top.ID)"
}
prove -property {top.v_top.ast_has_same_id_on_ID} -time_limit 2m -with_helpers
```

**Gotchas**:
- `-with_helpers` is **required** — omitting it ignores declared helpers
- `assert -mark_proven helper`: injects externally verified result (soundness depends on external proof)
- Loop-generated helpers must escape `[` and `]` in Tcl strings
- If helper dependencies become hard to audit, move the same obligations into
  `proof_structure` and require the propagated ROOT result.

## SST-Guided Helper Refinement [JG-specific]

> 🔧 **VERSION-SENSITIVE — validated on JasperGold 2025.12p002.** Recheck
> `help prove` and `help visualize` before standardizing this flow on another
> release.
>
> ⚠️ **NEEDS VALIDATION — agent trigger/refinement efficacy awaits the manual
> blind A/B; the command and trace semantics below have been tool-validated.**

**Trigger**: Use this diagnostic flow when an invariant-like assertion remains
`undetermined` after a sane direct proof, no reset-reachable CEX exists, and a
missing relation among state variables is plausible. Typical signals are a deep
antecedent, slowly growing BMC bound, or a target that looks true only because
of history not stated in the property. SST also helps bypass irrelevant
initialization prefixes. Do not use it as a generic response to every timeout;
first correct reset/setup errors and identify obvious cone-size causes.

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

Inspect the exported waveform with the available waveform reader. Compare the
last prefix state with the failing state, then ask:

1. Which compact relation does reset establish and every RTL transition
   preserve, but the arbitrary SST start violates?
2. Would that relation exclude the whole impossible state family rather than
   only the literal values in this trace?
3. Is the candidate structurally simpler and more inductive than the target?

Prefer range, phase/order, mutual-exclusion, correlation, and conservation
relations over helpers that merely restate the target. Treat the trace as
negative feedback for candidate generation, not as evidence that the candidate
is true.

### Refine, Prove, Then Activate

Declare each candidate as a helper assertion and prove it from the same RTL,
clock, reset, and legal environment as the target. Do not add an assumption to
make the candidate pass.

If the candidate is `cex`, discard or weaken it using that reset-reachable
counterexample. If it remains `undetermined`, leave it inactive and run the
same SST diagnostic on the candidate; use the new SST trace to refine or split
the candidate. Keep this loop bounded and escalate to AG/CAG when the helper
graph becomes multi-stage or as hard as the target.

Activate only after an explicit status gate:

```tcl
assert -helper -name h_candidate {<candidate_invariant>}
prove -property h_candidate

set helper_status [get_property_info h_candidate -list status]
puts "HELPER_STATUS $helper_status"
if {$helper_status ne "proven"} {
  error "candidate is not independently proven; refusing set_helper"
}

assert -set_helper h_candidate
prove -property $target -with_helpers
```

Report the SST trace separately from proof results. A sound completion records:

- target status before refinement (`undetermined`, bound, engine, time);
- SST property status plus `trace_id`, trace length, and `tag SST`;
- every candidate helper result before activation;
- the status-gate evidence preceding `assert -set_helper`;
- final helper and target statuses, with `Infinite` bounds for full proof.

**Anti-patterns**:

- Calling an SST trace a reset-reachable bug or ordinary CEX.
- Saying “CTI” without disclosing that Jasper reported `tag SST`.
- Asking a model to infer a helper from `prove -sst` metadata without opening or
  exporting the trace.
- Promoting an SST-inspired candidate directly with `assert -set_helper`.
- Replacing independent helper proof with `assume` or `assert -mark_proven`.

## See Also
- Shrinking the cone before decomposing (stopat/cutpoints/free vars): `cone-reduction.md`
- Index, soundness rules, anti-patterns: `../complexity-management.md`
