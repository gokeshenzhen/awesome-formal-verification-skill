# Neutral JasperGold FPV task — two_counters

`two_counters.v` is the design under test (top module `test`). It contains two
32-bit registers, `counter1` and `counter2`, and one embedded SVA assertion.

## Task

Formally verify, with JasperGold, the **embedded assertion already in the RTL**:

```
assert property (@(posedge clk) &counter1 |-> &counter2);
```

- Reach a FULL (unbounded) proof of that assertion, or clearly show you cannot.
- Also demonstrate the assertion is not vacuous (its antecedent is reachable).

## Rules

- Do NOT edit `two_counters.v`. Treat it as the fixed design under test.
- If your final result depends on any added property, modeling assumption, or
  bind checker, prove it before relying on it and DISCLOSE it; do not call an
  assumption-dependent result an unqualified raw-RTL signoff.
- Do not read other directories, prior reports, or any solution material.
- Use batch JasperGold (`jg -batch`, timestamped `-proj` dirs).
