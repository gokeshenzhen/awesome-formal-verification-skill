# FPV Benchmark Scenarios

This directory contains test scenarios for validating the FPV skill modules.

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
- [ ] Prove the helper from the same RTL/setup without helper-specific assumptions before `assert -set_helper`
- [ ] Abort or escalate if the helper is not `proven`; use `-with_helpers` only after the gate
- [ ] Escalate to AG/CAG if the helper remains undetermined or is as hard as the targets

### Anti-Patterns to Avoid
- Selecting CAG solely because the properties are global, uniqueness, or no-duplicate
- Activating an undetermined helper

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
