# Complexity: Targeted Reduction Knobs

> Leaf of `complexity-management.md`. Smaller, targeted levers that reduce complexity without restructuring the model: per-property simplification settings and clock-ratio control.

## Per-Property Simplification

**When to use**: One specific property in a task is far harder than the rest and is dragging the whole run down. You want heavier simplification applied to that property's logic only, leveraging its preconditions, without changing how the other properties are handled.

**Template**:
```tcl
set_per_property_simplification on    ;# precondition-based simplification, per property
# ... then prove; each property is simplified using its own preconditions
prove -property <hard_prop>
set_per_property_simplification off   ;# restore default when done
```

**Key insight**: Per-property simplification uses each property's preconditions (constant propagation, precondition-implied constants) to simplify the logic in *that property's* cone — so a property guarded by a strong precondition gets a much smaller model than a global simplification would produce.

**Related global knobs** (broader, not per-property):
```tcl
set_prove_advanced_simplification on   ;# advanced simplification across the task
set_word_level_reduction on            ;# word-level (vs bit-level) reasoning
```

**Gotchas**:
- It is a per-property *preference* — pair it with the right engine/time-limit choices for the hard property (see `engine-tuning.md`).
- When constant propagation or preconditions are unlikely to simplify the logic, it adds little; profile first.

## Clock Ratio Management

**When to use**: Multi-clock designs where async proofs need robustness across static clock ratios.

**Template**:
```tcl
clock clk_a -from 1 -to 2 -both_edges
clock clk_b -from 1 -to 2 -both_edges
```

**Gotchas**:
- Start with fixed ratios; widen to ranges only after fixed-factor bugs are resolved
- `-both_edges` + range → search space expands over both factor and phase
- Does NOT model dynamic frequency/phase changes between cycles
- `set_prove_clock_optimization on` reduces multi-clock scheduling overhead

## See Also
- Engine selection / time limits for the hard property: `../engine-tuning.md`
- Index, decision tree, core rules: `../complexity-management.md`
