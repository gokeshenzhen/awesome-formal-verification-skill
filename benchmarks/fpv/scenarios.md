# FPV Benchmark Scenarios

This directory contains test scenarios for validating the FPV skill modules.

## Scenario: sst-proven-support-selection [control]

### Category

complexity-management

### User Prompt

"A payload helper is undetermined despite an explicitly selected, valid proven
control invariant. I start a fresh JasperGold diagnostic and run prove -property
h_payload -sst 2 without recreating or selecting that support. Its SST trace
violates the control invariant. Should I invent another helper from this trace?
Give the next diagnostic setup, exact support selection shape, and evidence
needed before interpreting it."

### Modules That Should Be Consulted

- knowledge/fpv/complexity-management/sst-refinement.md

### Expected Key Points

- [ ] Recreate and validly prove the support in the current unchanged task
- [ ] Select target and support together for `prove -sst`; record their names
- [ ] Account for all enabled helper/SST properties' prefix roles, not just the explicit list
- [ ] Do not duplicate a known invariant simply because an unsupported diagnostic violates it
- [ ] Confirm `tag SST` and read concrete transition values; normal proof gates still apply

## Scenario: helper-refinement-engine-control [control]

### Category

complexity-management

### User Prompt

"After reading a JasperGold SST waveform, I added a plausible state invariant
and proved it under the unchanged environment. For the payload helper retry I
also replaced the original mixed engine portfolio with the smaller portfolio
that was fast on the control lemmas. The payload helper is still undetermined.
Does this refute the refinement? What bounded comparison should I run before
abandoning it, which settings should be preserved, and what must still be proved?"

### Modules That Should Be Consulted

- knowledge/fpv/complexity-management/sst-refinement.md
- knowledge/fpv/complexity-management/decomposition.md

### Expected Key Points

- [ ] Do not infer a false relation or ineffective refinement from an inconclusive run
- [ ] Restore the original ordinary engine portfolio and limit for a comparable refined trial
- [ ] Change engine choice separately; a control-lemma winner may be poor for payload reasoning
- [ ] Record expressions, selected proven support, engine mode and time limits before/after
- [ ] Prove the helper and original target normally within the total budget
- [ ] Keep SST's diagnostic engine choice separate from the ordinary proof portfolio

## Scenario: helper-trial-result-budget-branch [control]

### Category

complexity-management

### User Prompt

"A JasperGold baseline has already timed out on an invariant-like target. I have
a plausible compact helper, but it has not been proved. My next Tcl script queues
a long helper trial followed unconditionally by a longer target retry with
-with_proven, spending the remaining budget. If the helper is undetermined and
has no reset-reachable CEX, is that a useful recovery plan? Give the
result-dependent next steps, budget reservation, diagnostic evidence, and proof
gates. Must a helper that succeeds immediately still undergo diagnostics?"

### Modules That Should Be Consulted

- knowledge/fpv/complexity-management/decomposition.md
- knowledge/fpv/complexity-management/sst-refinement.md

### Expected Key Points

- [ ] Branch on actual helper status; an unproved helper adds no theorem to `-with_proven`
- [ ] Record `HELPER_DECISION` before the next run, including final-script preparation; a new filename is not a new strategy
- [ ] Reserve diagnosis, revision and final-proof time before launching the trial
- [ ] Check selected support, then use capped SST when a missing relation remains plausible
- [ ] Read actual transition values and link them to a semantic revision, not just a command
- [ ] Prove the new obligations under unchanged setup before reuse in the original target
- [ ] Accept a sound first-candidate success without manufacturing retrospective diagnostics

### Anti-Patterns to Avoid

- Prequeueing unchanged target retries regardless of candidate outcome
- Adding benchmark-specific signals, formulas or desired waveform values
- Treating token checks as evidence of autonomous refinement and convergence

## Scenario: tcl-clocked-helper-syntax [control]

### Category

tcl-commands

### User Prompt

"In JasperGold 2025.12p002, assert -helper -name h {(@(posedge clk) disable iff
(!rst_n) (valid |-> data == expected))} fails near disable. The reset polarity
is intentional. How should I repair the Tcl declaration without changing the
property, and does this syntax repair count as a semantic helper refinement?"

### Modules That Should Be Consulted

- knowledge/fpv/tcl-commands.md

### Expected Key Points

- [ ] Put the clock and disable clauses directly inside Tcl braces
- [ ] Remove the parentheses around the entire clocked property; preserve the body and reset
- [ ] Identify ENL063 as a declaration error; do not count a syntax repair as refinement

## Scenario: sst-partial-transition-readback [control]

### Category

complexity-management

### User Prompt

"A JasperGold helper remains undetermined. Its exported diagnostic trace is
tagged SST and contains a satisfying prefix followed by a violation. The
waveform reader returns only one clock-aligned sample, marks the response
truncated, and shows the helper bit low. I queried only the terms in the helper
expression; it uses fixed-width arithmetic. Have I inspected enough to refine
it? What should I read next, how should that evidence change the next proof
attempt, and what would count as a completed refinement?"

### Modules That Should Be Consulted

- knowledge/fpv/complexity-management.md
- knowledge/fpv/complexity-management/decomposition.md
- knowledge/fpv/complexity-management/sst-refinement.md

### Expected Key Points

- [ ] Read predecessor and failing state; explicitly fetch the initial timestamp if edge sampling omitted it
- [ ] Read RTL update enables, selection/priority conditions and source operands beyond the candidate expression
- [ ] Interpret fixed-width arithmetic and sampling correctly, not as an arbitrary-precision sum
- [ ] Link concrete values and the active update branch to a revised candidate or supporting lemma
- [ ] Prove new obligations before trusting them as theorems; keep `tag SST` separate from a reachable CEX
- [ ] If no useful relation emerges, report why and choose the next experiment; do not invent a helper for compliance
- [ ] A tool call, syntax fix, unchanged expression or promise is not evidence of completed refinement

### Anti-Patterns to Avoid

- Treating one returned sample or a pseudo-signal as a complete causal explanation
- Giving this generic scenario the signal names or solution from a development benchmark
- Counting token-pattern matches as proof of end-to-end behavioral efficacy

## How Benchmarks Work

Each scenario describes a realistic user prompt and the expected AI behavior. These are used to verify that the skill modules provide accurate, actionable guidance.

## Scenario Format

```markdown
## Scenario: [descriptive-name]

### Category
property-writing | engine-tuning | complexity | tcl | workflow

### User Prompt
"[What a real user would type]"

### Modules That Should Be Consulted
- knowledge/fpv/[module].md
- (other relevant modules)

### Expected Key Points
- [ ] Point 1 the AI should cover
- [ ] Point 2 the AI should cover

### Anti-Patterns to Avoid
- Wrong approach the AI should NOT suggest
```

## Running Benchmarks

For Claude Code: Use the skill-creator eval framework.
For other agents: Manually test each scenario and record results.

See `eval-runner.md` for detailed instructions.

---

## Scenarios

Each scenario marks its intent: **[control]** = the knowledge file covers this well
(skill should answer correctly), **[loss-probe]** = targets content the distillation
pipeline is known to have dropped (measures whether the loss causes a real task miss).
Run each with the skill loaded and without, and compare against the key-point checklist.

The token checks in `scenarios.json` are a screen, not a behavioral verdict.
Review the emitted script and evidence against these checklists; merely naming
`set_proven_directive` or `-with_helpers` does not establish correct dependency use.

---

## Scenario: helper-proven-support-selection  [control]

### Category

complexity

### User Prompt

"In one unchanged JasperGold task, h_a and h_b are valid proven assertions.
A higher-level h_summary remains undetermined after prove -property h_summary.
I marked h_a and h_b as helpers and assumed that this made them available
automatically. Before changing any invariant or budget, how do I check and reuse
only these two proven dependencies? Give the exact Tcl shape, status gates, and
evidence needed to distinguish actual reuse from another isolated attempt."

### Modules That Should Be Consulted

- knowledge/fpv/complexity-management.md
- knowledge/fpv/complexity-management/decomposition.md

### Expected Key Points

- [ ] Separate helper classification, valid proof status, and selected dependencies
- [ ] Keep the same task/setup and check each support with `get_property_info` before reuse
- [ ] Use `set_proven_directive true` and `prove -property {h_summary h_a h_b}` or the equivalent Tcl list
- [ ] Omit broad `-with_helpers` / `-with_proven` selection when exact support scope is required
- [ ] Audit before-call statuses, actual selection, `IPF036` counts, and the target's final status/validity/bounds
- [ ] Do not change the candidate or raise the budget before checking missing reuse

### Anti-Patterns to Avoid

- Assuming `assert -set_helper` proves a fact or automatically injects it into every later proof
- Checking the support list but passing only h_summary to `prove`
- Replacing an exact list with a Boolean toggle for `-with_helpers`

---

## Scenario: helper-batch-proof-audit  [control]

### Category

complexity

### User Prompt

"A JasperGold script declares h_a, h_b, and h_c with assert -helper before any
proof. Its wrapper receives support={h_a}, but uses only llength to choose
prove -property h_b -with_helpers. At this point h_a is proven; the log shows two
pending obligations plus one already-proven assertion, and h_b and h_c become
proven in the same call. A later h_c call has no pending obligations. The original
target has not been attempted. Is helper declaration before proof unsound? Did
the wrapper enforce its named support list, and may I report a sequential
h_a-to-h_b-to-h_c proof or full target signoff? Explain how to audit or make the
dependency scope exact."

### Modules That Should Be Consulted

- knowledge/fpv/complexity-management/decomposition.md

### Expected Key Points

- [ ] Helper classification is not proof or an unconditional assumption; declaring candidates is not itself unsound
- [ ] The wrapper did not enforce its list: `-with_helpers` included another unresolved helper
- [ ] Interpret h_b and h_c as batch-closed obligations, not proven sequentially in separate calls
- [ ] Treat the later h_c result as already proven, not a fresh independent proof
- [ ] Check valid per-property results and setup; do not call a tool-managed batch proof inherently circular
- [ ] Do not claim original-target signoff without the target's own completed proof
- [ ] For exact sequential reuse, gate supports with `get_property_info`, use `set_proven_directive true`, and pass the actual list to `prove -property`

### Anti-Patterns to Avoid

- Banning all `-with_helpers` calls that include unproven candidates
- Calling any helper batch a false proof, or claiming minimal dependencies from selection alone
- Mistaking wrapper argument names or a later cached result for the actual dependency history

---

## Scenario: helper-first-candidate-fast-path  [control]

### Category
complexity

### User Prompt
"A sane JasperGold baseline leaves one invariant-like target undetermined without
a reachable counterexample. Reading the RTL gives me a compact candidate relation
with a clear reset and update argument. No helper proof has been attempted. What
should I run next? Must I obtain a diagnostic waveform first, and what evidence is
needed before using the candidate to close the target?"

### Modules That Should Be Consulted
- knowledge/fpv/complexity-management.md
- knowledge/fpv/complexity-management/decomposition.md

### Expected Key Points
- [ ] Try a capped independent proof of the available candidate before diagnostics
- [ ] Preserve RTL/reset/environment; gate theorem reuse on valid `proven` status
- [ ] Select the proven support with an explicit list or disclosed helper selection; report the original target's own status
- [ ] If the first candidate succeeds, skip SST and report `refinement_not_exercised`

### Anti-Patterns to Avoid
- Requiring a deliberately failed first helper or a diagnostic waveform before proof
- Treating a candidate's success as evidence of trace-guided refinement

---

## Scenario: helper-feedback-classification  [control]

### Category
complexity

### User Prompt
"Two candidate helpers were independently attempted against unchanged raw RTL in
JasperGold. One has a reset-reachable CEX; the other is undetermined and an SST
trace shows an arbitrary initial state inconsistent with a suspected ownership
relation. How should the next candidate differ in each case, what evidence should
I preserve, and when can I activate it? Is either tool call alone proof that
feedback helped?"

### Modules That Should Be Consulted
- knowledge/fpv/complexity-management/decomposition.md

### Expected Key Points
- [ ] A raw reset-reachable CEX refutes the candidate, not necessarily the target
- [ ] `undetermined` does not refute it; a true but non-inductive relation may need support
- [ ] SST is arbitrary-state diagnostic evidence, not an exposed internal CTI or reachable bug
- [ ] Preserve old/new expressions, trace classification and actual state values that motivate revision
- [ ] Prove the revised candidate under the unchanged setup before theorem reuse; disclose any already-proven dependencies
- [ ] Tool use alone does not establish refinement or causal benefit

### Anti-Patterns to Avoid
- Weakening every undetermined candidate, or blocking just the literal trace values
- Adding environment assumptions to make the helper pass
- Trusting an unproven candidate as established or circularly assuming supporting lemmas

---

## Scenario: invariant-stall-routing  [control]

### Category
complexity

### User Prompt
"A sane JasperGold baseline leaves one same-cycle assertion comparing state
registers undetermined, with no reset-reachable counterexample or stored trace.
Reset and updates appear to maintain a relationship that the assertion does not
state. There is no obvious large-memory or setup issue, no suspected failure
window, and I do not yet know the missing relation. I want the strongest sound
conclusion within a finite budget. Which investigation should come next, what
evidence should I inspect, and when may a new fact be used in the final proof?"

### Modules That Should Be Consulted
- knowledge/fpv/complexity-management.md
- knowledge/fpv/complexity-management/decomposition.md

### Expected Key Points
- [ ] Route to a capped SST diagnostic before ordinary deepening; no finished helper is needed to select the route
- [ ] Do not select DBH solely from "strongest sound conclusion" or the finite budget
- [ ] Query status and trace ID separately, confirm `tag SST`, then inspect waveform values
- [ ] Classify SST as arbitrary-state diagnostic evidence, not a reset-reachable bug or exposed IC3/PDR CTI
- [ ] Prove candidates and gate on valid `proven` status before theorem reuse; reserve time for the target
- [ ] Preserve explicit bug-search intent: the existing `dbh-stalled-bound` and `dbh-exact-cycle-stall` scenarios must still route to search

### Anti-Patterns to Avoid
- Spending the remaining budget on another ordinary trace-only run without state-relation diagnosis
- Assuming the waveform proves the candidate, or treating an undetermined helper as established
- Forcing SST onto explicit known-bug reproduction or a concrete failure-window investigation

---

## Scenario: counter-abstraction-timeout  [control]

### Category
complexity

### User Prompt
"My JasperGold proof is too deep to converge because the DUT has a 32-bit timeout counter that has to count to a large value before the interesting behavior happens. How do I abstract it?"

### Modules That Should Be Consulted
- knowledge/fpv/complexity-management.md

### Expected Key Points
- [ ] Use counter abstraction — `abstract -counter` (discovery vs signoff)
- [ ] Discovery pass first (`abstract -counter -find` / zero-effort), then explicit milestone abstraction for signoff
- [ ] Abstract at the milestone value(s) the property cares about, not the full range
- [ ] Consider disabling abstraction during reset

### Anti-Patterns to Avoid
- Leaving the full-width counter in the cone of influence and just switching engines
- Blindly black-boxing the whole counter logic, losing the milestone behavior

---

## Scenario: config-logic-cutpoint  [loss-probe]

### Category
complexity

### User Prompt
"In JasperGold my proof blows up because the design's configuration logic dominates the cone of influence. The configuration is written once at init and then held stable. How do I cut this complexity without producing false failures?"

### Modules That Should Be Consulted
- knowledge/fpv/complexity-management.md

### Expected Key Points
- [ ] Place **cutpoints** on the internal configuration signals to remove the config-generation logic from the COI
- [ ] Pair the cutpoints with **legality/validity assumptions** — convert configuration-validity checks into assumptions so the proof only explores *legal* configurations
- [ ] Mention the mechanism (e.g. `setup_ndc`) for making a cut signal non-deterministic but legally constrained

### Anti-Patterns to Avoid
- Cutpointing the config signals **without** constraining them to legal values → proof explores impossible/invalid configurations → spurious counterexamples
- Recommending only generic abstraction/black-boxing without the cutpoint + legality-assumption pairing

> Ground truth: complexity-management extractions describe "Configuration Cutpoints with
> Legality Assumptions". The current 500-line knowledge file dropped this (loss_probe
> flags `cutpoint` and `setup_ndc` as absent). This scenario measures the task impact.

---

## Scenario: per-property-simplification  [loss-probe]

### Category
complexity

### User Prompt
"One specific property in my JasperGold task is far harder than the rest and is dragging the whole run down. Is there a way to apply heavier simplification just to that property without changing the others?"

### Modules That Should Be Consulted
- knowledge/fpv/complexity-management.md

### Expected Key Points
- [ ] Apply per-property simplification — e.g. `set_per_property_simplification` — to spend more reduction effort on the hard property only
- [ ] Frame it as targeting the single hard property rather than the whole task

### Anti-Patterns to Avoid
- Only suggesting a global engine/time-limit change that affects every property

> Ground truth: `set_per_property_simplification` appears across 4 extractions but is
> absent from every knowledge file (loss_probe REAL LOSS). Measures task impact.

---

## Scenario: proof-decomposition-ag  [control]

### Category
complexity

### User Prompt
"A single assertion in JasperGold won't converge. I think I need to break the proof into smaller pieces and prove them separately. How does assume-guarantee work here and how do I keep it sound?"

### Modules That Should Be Consulted
- knowledge/fpv/complexity-management.md

### Expected Key Points
- [ ] Use assume-guarantee / CAG decomposition — prove helper lemmas, then use them as assumptions for the target
- [ ] Keep it **sound**: the ROOT/target result is the sound one; helpers used as assumptions must themselves be proven
- [ ] Staged flow (prove helpers first, then the target using proven helpers)

### Anti-Patterns to Avoid
- Treating a helper that is only assumed (not proven) as a sound result
- Circular assume-guarantee where a helper assumes the very thing it helps prove

---

## Scenario: compact-global-helper  [control]

### Category
complexity

### User Prompt
"After a sane direct JasperGold prove, 412 generated no-duplicate assertions remain undetermined with no counterexample. I can state one global uniqueness invariant that may summarize the missing fact. How should I choose between a helper assertion and CAG, what gates make the result sound, and what are the exact key JasperGold Tcl commands for activating and using the helper?"

### Modules That Should Be Consulted
- knowledge/fpv/complexity-management.md
- knowledge/fpv/complexity-management/decomposition.md

### Expected Key Points
- [ ] Treat the property labels as a complexity trigger, not a mandatory CAG choice
- [ ] Try one bounded compact helper because one global invariant may summarize the dependency
- [ ] Prove the helper from the same RTL/setup without helper-specific assumptions before trusting it as a theorem
- [ ] Gate sequential reuse on valid `proven` status; explicitly select support or disclose the broader `-with_helpers` set
- [ ] Escalate to AG/CAG if the helper remains undetermined or is as hard as the targets

### Anti-Patterns to Avoid
- Selecting CAG solely because the properties are global, uniqueness, or no-duplicate
- Mistaking helper classification for proof, or trusting an undetermined helper as established

---

## Scenario: distributed-peer-cag  [control]

### Category
complexity

### User Prompt
"A JasperGold proof has hundreds of symmetric peer no-duplicate obligations. A compact helper was tried in isolation but remains undetermined and has essentially the same cone as the targets. What proof shape should I use next, which result is valid for signoff, and what is the exact key JasperGold Tcl command that creates this decomposition?"

### Modules That Should Be Consulted
- knowledge/fpv/complexity-management.md
- knowledge/fpv/complexity-management/decomposition.md

### Expected Key Points
- [ ] Stop extending the failed helper trial
- [ ] Use compositional assume-guarantee with `proof_structure -create compositional_assume_guarantee`
- [ ] Build the CAG property set from the symmetric peer obligations
- [ ] Propagate/unify the result and use only the propagated `ROOT` status for signoff

### Anti-Patterns to Avoid
- Continuing to increase the helper time limit despite an unchanged proof cone
- Reporting a local CAG node as the sound top-level result

---

## Scenario: mem-abstraction-stall  [control]

### Category
complexity

### User Prompt
"In JasperGold my `prove -all` proves the top controller assertion and covers every cover, but one embedded assertion is stuck: it is an arbitrary symbolic-address write-then-read property over a real 512x32 memory array, and it stays undetermined — multiple engines hit their per-property time limits with no counterexample. The RTL must stay unchanged. What should I do, and how do I report the result honestly?"

### Modules That Should Be Consulted
- knowledge/fpv/complexity-management.md
- knowledge/fpv/complexity-management/abstraction.md

### Expected Key Points
- [ ] Recognize the stall signature (big array flops + arbitrary-address assertion + precondition cover reachable + no CEX) as the **memory-abstraction trigger** — stop re-racing engines
- [ ] Black-box only the array **instance** by path (`-bbox_i <path>`, not `-bbox_m`) so the original hierarchy is preserved
- [ ] Reconnect a **single symbolic slot** keyed to the property's own `$stable`/NDC address (e.g. a `bind`-ed one-word tracker + a reconnect `assume`)
- [ ] Prove the precondition cover for **non-vacuity**
- [ ] Report it as a **disclosed trusted-abstraction** result, NOT an unqualified raw-RTL signoff; to upgrade, discharge the reconnect contract against the real array

### Anti-Patterns to Avoid
- Continuing to re-race / re-tune engines on the full concrete array instead of abstracting
- Rewriting / replacing the memory module and reporting it as original-RTL signoff
- Black-boxing the array **without** reconnecting an abstract model → outputs fully unconstrained
- Assuming the controller property closing fast means the inner array property will

> Ground truth: this was a real skill gap (the memory-abstraction atoms existed only as a
> static reference, with no stall trigger and no signoff-discipline note). Fixed 2026-06-24 in
> `complexity-management/abstraction.md` (trigger checklist + symbolic-slot recipe + signoff
> discipline) and the index decision tree. A blind agent given only the updated skill then
> independently proved the stalled `mem_works_ndc` (test/mem_ctrl_orig). Now a **control**:
> this scenario guards against regressing that trigger+recipe back into a dropped gap.

---

## Scenario: dbh-stalled-bound  [control]

### Category
engine-tuning

### User Prompt
"A meaningful JasperGold prove is still undetermined at a finite bound. I need to search deeper for bugs now, but I must not misreport the result as signoff. Which DBH modes should I start with, what Tcl shape configures them, and what does a no-hit run mean?"

### Modules That Should Be Consulted
- knowledge/fpv/engine-tuning.md
- knowledge/fpv/engine-tuning/bug-hunting.md

### Expected Key Points
- [ ] Start with Cycle Swarm for a hard frontier cycle, Bound Swarm for a bounded range, and AUTO for state/path diversity
- [ ] Configure a named strategy with `hunt -config -strategy ... -mode ...`, then execute it with `hunt -run -strategy ...`
- [ ] Use `-first_trace_attempt`; bound a Bound Swarm range with `-max_trace_length`
- [ ] Treat CEX/covered traces as useful results, but preserve `undetermined` after a no-hit run
- [ ] Return to exhaustive `prove` plus complexity reduction for proven/unreachable signoff

### Anti-Patterns to Avoid
- Reporting a no-hit DBH run as proof that no bug exists
- Only increasing the global proof timeout without matching the Hunt mode to the complexity shape

---

## Scenario: dbh-activation-gate  [control]

### Category
engine-tuning

### User Prompt
"A bounded trace-only JasperGold Engine B run stopped at its finite maximum trace
length with the assertion still undetermined. In one design RTL analysis gives a
credible narrow next-depth interval; in another the depth is unknown and direct
deepening has already missed. When is one deeper B run appropriate, when must I
activate DBH, and what artifacts prove that I actually ran DBH?"

### Modules That Should Be Consulted
- knowledge/fpv/engine-tuning.md
- knowledge/fpv/engine-tuning/bug-hunting.md

### Expected Key Points
- [ ] Classify the finite B run as bounded trace search, not meaningful exhaustive proof
- [ ] Allow one cheap focused B/Hts extension for a credible narrow interval, but do not call it DBH
- [ ] Activate DBH for unknown/broad depth, repeated direct misses, uneven cycle complexity, competing targets, or diversity
- [ ] Execute and preserve a named `hunt -config` + `hunt -run` strategy (or AUTO), including tag/seed/resolved settings
- [ ] Preserve `undetermined` after a no-hit run; DBH does not provide signoff

### Anti-Patterns to Avoid
- Claiming that reading DBH guidance followed by only `prove -max_trace_length` constitutes DBH execution
- Forcing Hunt when one deterministic bounded extension is clearly the cheapest decisive experiment

---

## Scenario: dbh-exact-cycle-stall  [control]

### Category
engine-tuning

### User Prompt
"A capped JasperGold Engine B run starts and ends at `Trace Attempt 250` even
though `max_trace_length` is 252. RTL analysis suggests the first violation
sample may be at 250, 251, or 252 because of reset/SVA timing, while
input-controlled skips allow later sparse depths. I need the strongest sound
conclusion within a limited investigation budget. An earlier exploratory Jasper
run completed but will not appear in my final report. What should I run next,
and what exact Jasper Tcl and evidence should I preserve?"

### Modules That Should Be Consulted
- knowledge/fpv/engine-tuning.md
- knowledge/fpv/engine-tuning/bug-hunting.md

### Expected Key Points
- [ ] Classify unchanged first/last `Trace Attempt` as an exact-cycle stall
- [ ] Classify a strongest-conclusion finite-budget task as `mixed`, then fill `DBH_DECISION` before the next Tcl
- [ ] Record explicit candidate cycles separately from the broad/sparse fallback, plus elapsed/remaining wall time, reserved Hunt budget, and next action
- [ ] State that `-max_trace_length` is a ceiling, not a scheduler over adjacent candidates
- [ ] Run Cycle Swarm first with the explicit candidate list and per-attempt time limit; use Bound Swarm only as the later broad/sparse fallback
- [ ] Treat `-max_first_trace_attempt` as the maximum parallel attempt-group count, not a cycle number
- [ ] Count completed exploratory/discarded runs using process wall time; reserve Hunt budget and switch after one focused miss/stall
- [ ] Use `hunt -config`, `hunt -show -strategy`, and `hunt -run`; archive tag, seed, `IHT002`, Trace Attempt, `IPF180`, and final status

### Anti-Patterns to Avoid
- Extending the same focused B job because its `max_trace_length` includes neighboring cycles
- Collapsing explicit near-term candidates and a sparse fallback into one broad range
- Setting `-max_first_trace_attempt` to the maximum cycle
- Spending the reserved Hunt slice on another direct run, or excluding an already completed exploratory run from the wall-time ledger

---

## Scenario: dbh-known-bug-reproduction  [control]

### Category
engine-tuning

### User Prompt
"I have an external failing trace for a JasperGold target. I want to reproduce the bug, preserve useful steering states, then challenge the RTL fix with diverse paths. What DBH flow and exact commands should I use?"

### Modules That Should Be Consulted
- knowledge/fpv/engine-tuning.md
- knowledge/fpv/engine-tuning/bug-hunting.md

### Expected Key Points
- [ ] Qualify the trace against the current design/environment with `visualize -confirm` and evaluate assumptions/assertions/covers
- [ ] Ensure an assertion expresses the failure signature; fix assumptions that reject legal trace behavior
- [ ] Retain multiple high-value traces with `assert -set_store_trace unlimited` / `cover -set_store_trace unlimited`
- [ ] Reuse hit helpers with `hunt -run -auto`; after the fix add generated helpers via `-auto_helper_num` and preserve prior results with `-force`
- [ ] Report failure to rediscover as added search confidence, not proof of the fix

### Anti-Patterns to Avoid
- Loading an incompatible external trace without consistency checking
- Treating one successful replay path, or one post-fix no-hit seed, as exhaustive validation

---

## Scenario: dbh-regression-coverage  [control]

### Category
workflow

### User Prompt
"In a JasperGold regression, previously proven properties are now slow, an old CEX has not reappeared, and several critical coverage items remain uncovered. How should I carry history into DBH and close reachable coverage without claiming unreachability? Include the exact key Tcl commands."

### Modules That Should Be Consulted
- knowledge/fpv/engine-tuning.md
- knowledge/fpv/engine-tuning/bug-hunting.md
- knowledge/fpv/workflow.md

### Expected Key Points
- [ ] Persist/compare prior status, bound, and proof time with `report -csv`
- [ ] Use Cycle Swarm near the old proof effort, and Bound Swarm through the previous CEX depth plus an architecturally chosen margin
- [ ] Convert selected uncovered COV items to FPV covers with `check_cov -create_cover_item_property`
- [ ] Hunt the generated covers, rerun `check_cov -measure -refresh`, and track covered/CEX/trace diversity
- [ ] Keep uncovered items and no-hit hunts separate from exhaustive unreachable/signoff conclusions

### Anti-Patterns to Avoid
- Copying one lab's `+20` depth or 50%/70% timing as a universal project threshold
- Calling an uncovered item unreachable because DBH did not cover it

---

## Scenario: tcl-silent-command-grammar  [control]

### Category
Tcl commands

### User Prompt
"I am scripting JasperGold and want clean Tcl return values. May I append
`-silent` to every command, including a Hunt strategy-list command? How should
I decide when the option is legal?"

### Modules That Should Be Consulted
- knowledge/fpv/tcl-commands.md
- tool-specific/jaspergold/quirks.md

### Expected Key Points
- [ ] Use `-silent` only when the exact command form supports it; installed help and exact templates override a general scripting idiom
- [ ] On the validated release, use `hunt -list strategy` without `-silent`
- [ ] Do not infer that the option is valid for every Hunt subcommand

### Anti-Patterns to Avoid
- Appending `-silent` blindly and treating an invalid-command error as a proof or Hunt failure

---

## Scenario: dbh-stored-trace-continuation  [control]

### Category
engine-tuning

### User Prompt
"A JasperGold cover had a long legal trace in a prior run, while a target
assertion remains undetermined. The trace removes most of the deterministic
prefix to the suspected failure region, but a standalone replay starts a fresh
analysis session. What should I do before reset-based Swarm search, which exact
Tcl commands query and continue from that trace, when should the target search
stop, and what does a no-hit establish?"

### Modules That Should Be Consulted
- knowledge/fpv/engine-tuning.md
- knowledge/fpv/engine-tuning/bug-hunting.md

### Expected Key Points
- [ ] Distinguish prior-run trace evidence from a trace usable in the current session; query `status`, `trace_id`, and `trace_length`
- [ ] If the source property/trace is absent, recreate or run it in the same session and environment, then re-query it
- [ ] Continue the target with `prove -from`, `-trace_id`, `-cycle -1`, and an appropriate trace engine/budget
- [ ] Treat a found CEX as terminal for the target search with no follow-up Hunt; preserve `undetermined` after no hit

### Anti-Patterns to Avoid
- Assuming a no-hit `prove -from` run proves the target or makes a cover unreachable
- Treating a historical trace report, missing trace ID, or command failure as a valid current-session no-hit
- Running Hunt only to demonstrate DBH after continuation already found the target CEX

---

## Scenario: dbh-trace-first-probe  [control]

### Category
engine-tuning

### User Prompt
"A meaningful JasperGold prove left a target assertion undetermined, and the
baseline produced several legal cover traces. One trace is long but only
loosely related to the suspected failure region. A reset-based B or Swarm run
could consume most of the remaining investigation budget. Give me the ordered
next experiments and exact Tcl shape: how should I select and qualify a source,
budget the first continuation, react when it makes no quick progress, and keep
the result sound?"

### Modules That Should Be Consulted
- knowledge/fpv/engine-tuning.md
- knowledge/fpv/engine-tuning/bug-hunting.md

### Expected Key Points
- [ ] Inventory and qualify current-session traces before any reset-originating focused B/Hts, bounded, or Hunt search
- [ ] Rank sources by target/endpoint relevance, remaining suffix, and cone cost rather than trace length alone
- [ ] Use a predeclared capped `prove -from` probe with an expected suffix/progress criterion; do not give the first generic trace most of the budget
- [ ] On no quick progress, inspect the target cone/source endpoint and derive a reset-reachable observational milestone nearer the failure region with a smaller cone
- [ ] Cover and qualify that milestone under the unchanged environment before reusing its trace; add no assumption or behavioral restriction
- [ ] Stop on CEX; otherwise preserve `undetermined` and route a broad suffix to Trace Swarm/Search or justified reset-based DBH

### Anti-Patterns to Avoid
- Running reset-based bounded deepening before inspecting usable traces
- Repeatedly increasing the timeout on a long but weakly related source
- Treating an observational milestone as proof, a constraint, or a case split

---

## Scenario: dbh-bound-swarm-budget  [control]

### Category
engine-tuning

### User Prompt
"I want a JasperGold Bound Swarm over a broad depth range with several jobs and
increasing per-attempt effort. Before launching it, how do I determine whether
each job can reach the intended effort tier within the strategy time limit and
whether the whole portfolio fits my remaining compute budget? Which evidence
is available before launch, and which log records exist only after the run?"

### Modules That Should Be Consulted
- knowledge/fpv/engine-tuning.md
- knowledge/fpv/engine-tuning/bug-hunting.md

### Expected Key Points
- [ ] Calculate assigned cycles times the sum of all intended effort tiers per job, then sum jobs for aggregate slot-second demand
- [ ] Compare per-job work with the time limit and aggregate work with remaining budget before launch
- [ ] Use `hunt -config` plus `hunt -show -strategy` for pre-run inspection; `IHT002` is post-`hunt -run`, not feasibility evidence
- [ ] Archive `IHT002`, Trace Attempt, `IPF180`, and final status after the run
- [ ] Narrow with evidence, use a trace-directed method, or report a partial exploration when the intended tier cannot fit

### Anti-Patterns to Avoid
- Calling a timed-out partial scan a full-range rescan
- Using `IHT002` as a pre-launch budget gate
- Copying one example range, job count, or effort factor as a default
