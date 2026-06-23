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
