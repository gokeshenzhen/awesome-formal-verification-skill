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

(Scenarios will be added as knowledge modules are populated)
