# Neutral JasperGold FPV task — cnt_abstract_eg

`cnt_abstract_eg.sv` is the design under test (top module `cnt_abstract_eg`). It
is a small RTL block with a free-running internal counter and four single-bit
outputs `A`, `B`, `C`, `D`.

## Task

Formally verify, with JasperGold, that the outputs behave as the RTL intends:

- Derive the intended behaviour of `A`, `B`, `C`, `D` from the RTL itself.
- Write the SVA properties that capture that intent and PROVE them.
- Also demonstrate that the conditions which make each output become `1` are
  actually reachable (i.e. your passing properties are not vacuous).

## Rules

- Do NOT edit `cnt_abstract_eg.sv`. Treat it as the fixed design under test.
- If your final result depends on any modeling assumption, bind/helper checker,
  or design transformation, prove helpers before relying on them and DISCLOSE
  the assumption; do not call a transformed-design result an unqualified
  raw-RTL signoff.
- Do not read other directories, prior reports, or any solution material.
- Use batch JasperGold (`jg -batch`, timestamped `-proj` dirs).
