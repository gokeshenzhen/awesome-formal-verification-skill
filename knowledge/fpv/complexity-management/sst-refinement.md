# Complexity: SST-Guided Helper Refinement [JG-specific]

> 🔧 **VERSION-SENSITIVE — validated on JasperGold 2025.12p002.** Recheck
> `help prove`, `help sst`, and `help visualize` before standardizing this flow on another
> release.
>
> ⚠️ **NEEDS VALIDATION — command/trace semantics are tool-validated; a successful
> first candidate or an SST call alone does not validate refinement efficacy.**

**Trigger**: Use SST when an invariant-like assertion stays `undetermined`, no
reset-reachable CEX exists, and a missing state relation is plausible (deep
antecedent, slow BMC progress, or unstated history). SST can bypass irrelevant
initialization prefixes. First correct reset/setup errors and inspect cone size;
do not use it for every timeout.

### Choose the Entry Point

| Evidence available now | Next experiment |
|---|---|
| Clear compact candidate from RTL | Independently prove it with a capped budget; skip SST if it proves |
| No reasonable compact candidate | Diagnose the target with capped SST and inspect its state values |
| Diagnostic identifies a small state cluster, but no clear relation | Try capped `sst -generate -no_helper`; independently prove any generated candidates |
| Candidate has a reset-reachable CEX in the unchanged model | Inspect that CEX; correct, weaken, or replace the false candidate |
| Candidate remains `undetermined`, missing support is plausible | Do not trust it as a theorem; check selection of any already-proven support, then use capped SST/refinement if needed |
| Local data equality stalls despite proven count/index support | Use **Data-Correspondence Strengthening** in `decomposition.md`; reserve a structural trial before unchanged retries |
| Compact strengthening remains as hard as the target or needs a large dependency graph | Escalate to AG/CAG instead of repeating diagnostics |

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

After a candidate trial stalls, diagnose that candidate before spending another
full timeout on an unchanged target with no newly proven support. Reserve time
to read the trace, revise the relation, and run ordinary reset-based proofs.
If setup/support can be retained in the same Jasper session, a capped diagnostic
there can avoid a fresh compile; still archive the old expression and results.
Do not prewrite the final proof branch as though the candidate had succeeded.

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

### Tool-Assisted Candidate Generation

When the transition suggests a relation over a **small set of state signals**,
but its expression is unclear, try a capped search instead of guessing more
formulas. Avoid indiscriminately enumerating wide payloads or whole memories.

```tcl
set generated [sst -generate -signals {<state_signals>} -name generated_relation \
  -file /absolute/path/generated_values.dat -time_limit <budget> -no_helper -decompose]
puts "SST_GENERATED $generated"
```

Inspect returned `properties` using `get_property_info -list expression`.
`-decompose` requests smaller clauses; `-no_helper` leaves candidates unmarked.
Generation is **not proof**: prove under unchanged reset/environment, separately
or as an audited batch, before reuse. No candidates is an unresolved search.

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
loop bounded and escalate to AG/CAG when dependencies become hard to manage or
proofs remain as hard as the target despite selected support.

After valid proven helpers are enabled, check whether they exclude the archived
diagnostic with `sst -check -property $target -trace_id $trace_id`. Preserve the
raw result and original waveform before optionally adding `-clear` to remove
invalid trace associations. 🔧 2025.12p002 can return an outer list, not a direct
Tcl dictionary. Without `-clear`, another `prove -sst` can still report an old
attached trace; inspect the new result and metadata before calling it new feedback.
Invalidating an SST is not proof of the candidate or target; retain normal proof gates.

**Budget trigger**: if proven support excludes one SST but proof still stalls, try a short
follow-up `prove -sst` under accumulated proven support before another full ordinary-proof
timeout. Archive/clear invalid trace associations first; new states may suggest another helper.
This optional triage need not eliminate every SST. Reserve time for normal reset-based proof.

Use informative feedback for a bounded evidence-linked trial; if none is justified or budget
is exhausted, report that instead. Syntax fixes, unchanged retries and promises are not refinement.
Distinguish RTL-only discovery from trace-driven revision; do not invent helpers for a checklist.

Use the `prove_with_support` procedure in `decomposition.md` for each revised candidate
and the final target. `$candidate_support` names its already-proven dependencies;
use `{}` only when none are selected:

```tcl
assert -helper -name h_candidate {<candidate_invariant>}
prove_with_support h_candidate $candidate_support $helper_budget
prove_with_support $target [linsert $candidate_support 0 h_candidate] $target_budget
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

- `decomposition.md`: helper support selection, data correspondence, AG/CAG
- `../complexity-management.md`: complexity triage and cross-cutting soundness rules
