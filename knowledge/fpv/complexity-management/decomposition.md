# Complexity: Proof Decomposition

> Leaf of `complexity-management.md`. Break one hard proof into smaller obligations: helper lemmas, assume-guarantee / compositional AG, and state-space tunneling. When using `proof_structure`, require the propagated ROOT result for signoff, not just local node results.

## Helper vs. Proof Structure Decision

Use the lightest sound decomposition first, then escalate when signoff or scale
requires structure:

```
Direct proof stalls?
├─ Relevant support already proven? ......... Yes → check selection for the CURRENT obligation
│    helper or final target → "Helper Assertions" below
├─ Can one/few inductive invariants summarize
│  the missing local or global fact? ........ Yes → bounded helper trial
│    select support → prove obligation → gate on proven → next obligation
├─ Local data equality still undetermined with valid selected support?
│    → Data-Correspondence Strengthening before another unchanged proof
├─ Candidate CEX / undetermined? ............ Yes → do not trust as a theorem; classify feedback
│    reachable CEX → revise; missing relation → capped SST/refinement below
├─ Dependency graph hard to audit? .......... Yes → proof_structure AG
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
reuse. **Independent does not mean alone**: use already-proven lemmas to prove
another helper, then use that helper to prove the final target. A small acyclic
chain does not require AG/CAG merely because it has several levels. The words
`global`, `uniqueness`, `conservation`, or `peer` identify a complexity risk;
they do not by themselves require CAG.

## Helper Assertions (Lemmas) [JG-specific]

**When to use**: Try a capped helper proof when a compact invariant can summarize
the missing fact. If relevant lemmas are already proven but a higher-level
helper or target stalls, check that call's selected support before changing the
expression or extending time.

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
proc prove_with_support {obligation support limit} {
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
  set result [prove -property $selected -per_property_time_limit_factor 0 \
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
prove_with_support h_local {} $helper_budget
prove_with_support h_summary {h_local} $helper_budget
prove_with_support $target {h_local h_summary} $target_budget
```

An inconclusive result stops sequential theorem reuse along that chain, not all
further investigation. Classify the result using the refinement flow below;
do not require failure or SST before accepting a proven first candidate. Do not
add an assumption merely to make a helper pass.

**Branch before spending the next budget.** Do not queue an unconditional long
target retry immediately after a trial helper. If the helper is still
`undetermined`, `-with_proven` gains no new theorem from it. Record its result,
check support selection, then choose the next experiment. For a plausible
missing state relation, read `sst-refinement.md` and reserve a capped diagnostic
and revised-helper proof before another unchanged target attempt. Otherwise,
record why this route is unsuitable and use the decision tree above.

Before launching a trial, allocate separate time for that trial, possible
diagnosis, revised obligations, and the final target, including tool startup.
Do not let a speculative candidate plus a prequeued target retry consume the
entire recovery budget. Keep scripts/expressions from each attempt; syntax
repairs are not semantic helper revisions.

Record a `HELPER_DECISION` before the next run: obligation, status/validity,
selected proven support, next action and its evidence, remaining budget, and
time reserved for diagnosis/revision and final proof. For an `undetermined`
candidate with plausible missing state support, select a short diagnostic
before an unchanged retry unless new proof evidence justifies that retry.
Preparing `final.tcl` is not an exemption: retain the current script for replay
and use the remaining investigation budget on the chosen evidence-producing
step. If stopping early, identify the concrete blocker or explain why no
useful investigation fits; merely reporting the same timeout is not that reason.

For the first feedback-driven retry, preserve the stalled obligation's ordinary
engine portfolio and limit while changing its relation/support. Judge engine
changes separately; a good control-lemma engine is not necessarily a good
payload engine. See `sst-refinement.md` → **Refine, Prove, Then Reuse**.

For an existing assertion, resolve its exact name before using the same template:

```tcl
set matches [get_property_list -include {name *uniqueness_inv*}]
if {[llength $matches] != 1} {error "resolve one exact helper name first"}
set helper [lindex $matches 0]
prove_with_support $helper $support $helper_budget
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

When a selected-entry or output-data equality remains hard after its control
relations prove, inspect what supplies that data on the **next** transition.
A head-only fact does not constrain the next stored entry when a pointer moves.
After a capped local trial, reserve a bounded structural trial before spending
the remaining budget on the unchanged helper or target. SST can inform this
trial; it is not a prerequisite when RTL already exposes the missing source.

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
# Use prove_with_support from "Helper Assertions" above; budgets are task inputs.
prove_with_support h_leaf {} $helper_budget
prove_with_support h_top {h_leaf} $helper_budget
prove_with_support target_prop {h_leaf h_top} $target_budget
```
Escalate this helper chain into `proof_structure` when its dependencies become
hard to manage, proofs remain hard despite support, or a ROOT report is required.

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

Read [`sst-refinement.md`](sst-refinement.md) for the candidate-result decision,
SST capture and waveform inspection, refinement, and normal-proof gates.
Use that route when no compact candidate is clear, or a capped candidate proof
remains `undetermined` and missing state support is plausible. A candidate CEX
instead calls for reachable-trace analysis. A successful first candidate needs
no retrospective SST; report `refinement_not_exercised`.

## See Also
- Shrinking the cone before decomposing (stopat/cutpoints/free vars): `cone-reduction.md`
- Index, soundness rules, anti-patterns: `../complexity-management.md`
