# FPV: Property Writing

> 🔬 **from-docs** — Generated from Cadence JasperGold documentation, 2026-06-14. Needs field validation.

## Overview

How to write SystemVerilog Assertions (SVA) that formal tools can evaluate *efficiently*. Formal supports only a curated subset of legal SVA; many constructs that simulate fine are slow or unsupported in formal. Consult this module when authoring `assert` / `assume` / `cover` properties, choosing operators, or deciding when to push temporal behavior into auxiliary HDL.

## Quick Decision Tree

```
Writing a property?
├─ What directive?
│   ├─ Must always hold ............... assert property
│   ├─ Constrain DUT inputs ........... assume property
│   └─ Show a scenario is reachable ... cover sequence   (pure sequence, no |-> / |=>)
│
├─ Consequent timing relative to antecedent?
│   ├─ same cycle antecedent completes . A |-> B
│   └─ next cycle ...................... A |=> B   ( ≡ A ##1 B |-> ... )
│
├─ Need history / repetition?
│   ├─ depth N small (<~10) ............ $past(expr,N) or seq[*N]
│   └─ depth large / unbounded ......... write AUXILIARY CODE (counter), not [->N]/[=N]
│
├─ Unbounded "eventually"? ............. s_eventually  (liveness)
│
└─ Clock?  (MANDATORY — SVA cannot be unclocked)
    ├─ at declaration:  property P; @(posedge clk) ...
    ├─ at instantiation: assert property (@(posedge clk) P);
    └─ scope default:    default clocking C @(posedge clk); endclocking
        (explicit always overrides default)
```

## Core Rules

1. **Every property must have a clock** — explicit at declaration, explicit at instantiation, or via `default clocking`. SVA properties cannot be unclocked. An explicit clock always overrides the default; a sequence with no clock inherits its parent property's clock.
2. **A property declaration checks nothing by itself.** It is only a definition of behavior. A *verification directive* — `assert`, `assume`, or `cover` — is what tells the tool to act.
3. **Stay inside the formal-friendly subset.** Avoid the "not recommended" constructs (see Anti-Pattern Reference); they are slow or unsupported in formal even though they are legal SVA.
4. **Never use GoTo `[->N]` or non-consecutive `[=N]` repetition in properties** — they create infinite-length sequences. Replace with auxiliary counter code.
5. **Keep bounded depth `N` small (below ~10)** for `seq[*N]` and `$past(expr, N)`; each cycle of depth adds proof state. Model deep history with auxiliary registers instead.
6. **Use one clock everywhere when the design is single-clock.** If the whole design uses `posedge clk`, put `@(posedge clk)` on *all* properties — it is more efficient for the tool than mixed clocks.
7. **Do not nest implication operators.** `A |=> B |=> C` is confusing and equivalent to the flattened `A ##1 B |=> C`.
8. **For `cover`, use a pure sequence body and `cover sequence`** — no `|->` / `|=>`. Cover wants a witness trace, not an obligation.
9. **Drop obligations on reset with `disable iff`.** Use `default disable iff` when many properties share the same condition; an explicit `disable iff` on a property overrides the default.
10. **Define a sequence's clock at instantiation, not at declaration.** A one-cycle sequence is identical to a Boolean expression.

## Pattern Catalog

### Parameterized property with reset disable
**When to use**: a reusable check applied across multiple signal sets, cancellable on reset.
**Template**:
```systemverilog
property NAME (args);
  @(posedge clk) disable iff (!rst_n)
    antecedent |=> consequent;
endproperty
LABEL : assert property (NAME(sig_a, sig_b, sig_c));
```
**Example**:
```systemverilog
property P1 (R, S, T);
  @(posedge clk) disable iff (!rst_n)
    A |=> R ##1 S && T;
endproperty
P1_INST : assert property (P1(SIG1, SIG2, S3));
```
**Gotchas**: `disable iff` acts *asynchronously* — it takes precedence over and is unrelated to the clocking expression. For synchronous abort semantics see `sync_accept_on` / `sync_reject_on` in the LRM.

### Liveness with `s_eventually`
**When to use**: "after a request, a grant must *eventually* occur," with no fixed cycle bound.
**Template**:
```systemverilog
property NAME;
  trigger |=> s_eventually response;
endproperty
```
**Example**:
```systemverilog
property P1A;
  REQ |=> s_eventually GNT;
endproperty
```
**Gotchas**: liveness proofs need engines/strategies suited to unbounded behavior — see `engine-tuning.md`. Pair with `disable iff` so reset cancels the outstanding obligation.

### Input constraint via `assume property`
**When to use**: restrict DUT inputs to legal environment behavior (a.k.a. constraints).
**Template**:
```systemverilog
LABEL : assume property (input_legality_expr);
```
**Example**:
```systemverilog
P4 : assume property (req && !gnt |=> req);            // hold req until granted
P5 : assume property (@(posedge clk3) not(full && empty));
```
**Gotchas**: an over-tight `assume` silently removes legal stimulus and can mask real bugs (vacuity). Keep assumptions minimal and review them.

### Cover a sequence (reachability witness)
**When to use**: prove a scenario can actually happen given the design + assumptions.
**Template**:
```systemverilog
LABEL : cover sequence (pure_sequence);   // no implication operators
```
**Example**:
```systemverilog
C1 : cover sequence (full ##[+] empty);
C2 : cover property (@(posedge clk2) (SEQ1));   // named/clocked sequence
```
**Gotchas**: do not put `|->` / `|=>` in a cover body; use `cover sequence`, not `cover property`, when the body is a bare sequence.

### Shared reset via `default disable iff`
**When to use**: many properties in a scope share the same disable condition.
**Template**:
```systemverilog
default disable iff (COND);
// properties without an explicit disable iff inherit COND
```
**Example**:
```systemverilog
default disable iff (CANCEL)
P10: assert property (@(posedge clk) disable iff (!rst_n) A |=> B); // !rst_n wins (explicit)
P11: assert property (@(posedge clk) C |=> D);                       // disabled by CANCEL
```
**Gotchas**: the default applies to the current scope only; explicit `disable iff` overrides it.

### Auxiliary code instead of GoTo repetition
**When to use**: replacing `A[->N]` (GoTo), which creates infinite-length sequences, with bounded state.
**Template**:
```systemverilog
// Count occurrences in HDL, then assert over the counter
reg [W-1:0] cnt;
always @(posedge CLK or negedge RST_N) /* update cnt */;
CHECK : assert property ( (cnt == TARGET) |-> consequent );
```
**Example**:
```systemverilog
// AVOID: assert property( GO |=> A[->3] ##1 B );   // unbounded
reg [2:0] NUM_A;   // count A's
reg       GO_SEEN; // flag: GO observed
always @(posedge CLK or negedge RST_N)
  if (!RST_N)              begin NUM_A <= 0; GO_SEEN <= 1'b0; end
  else if (NUM_A==3 && B)  begin NUM_A <= 0; GO_SEEN <= 1'b0; end
  else if (GO_SEEN && A)         NUM_A  <= NUM_A + 1;
  else if (GO)                   GO_SEEN <= 1'b1;
GO_3A_B     : assert property ( (NUM_A == 3) |-> B );
NO_OVRLAP_GO: assert property ( GO_SEEN |-> !GO );
```
**Gotchas**: "almost every problem in formal requires auxiliary code." Auxiliary HDL turns unbounded temporal patterns into bounded, tool-friendly state — this is property-authoring-time complexity reduction (see `complexity-management.md`).

## Anti-Pattern Reference

| Anti-Pattern | Why It Fails | Correct Alternative |
|-------------|-------------|-------------------|
| `throughout`, `and`, `or`, `within`, `intersect`, `first_match()`, `expect`, local variables, immediate assertions, `if property else property` | Not recommended for formal — slow or unsupported in the formal-friendly subset | Restrict to `##`, `\|->`/`\|=>`, `[*N]`; rewrite the property |
| `sequence[->N]` (GoTo) / `sequence[=N]` (non-consecutive) | Create infinite-length sequences → unbounded proof | Auxiliary counter code |
| Large `N` in `seq[*N]` or `$past(expr,N)` | Each cycle of depth adds proof state → blowup | Keep N < ~10; model history with auxiliary registers |
| Unclocked property | Illegal — nothing to sample on | Explicit clock, instantiation clock, or `default clocking` |
| Nested implication `A \|=> B \|=> C` | Confusing; surprising semantics | Flatten: `A ##1 B \|=> C` |
| `cover property` on a body with `\|->` / `\|=>` | Cover needs a witness sequence, not an obligation | Pure sequence body + `cover sequence` |
| Assuming `disable iff` follows the clock | It acts asynchronously, independent of the clock | Treat disable as taking precedence; use `sync_accept_on`/`sync_reject_on` if synchronous abort is needed |
| Over-tight `assume property` | Removes legal stimulus → vacuous pass, masked bugs | Keep assumptions minimal; review for vacuity |

## SVA Syntax Reference

Operator semantics (`|->` / `|=>`, cycle delays `##N`/`##[N:M]`), declaration forms,
clocking precedence, and the sampled-value/system functions (`$past`, `$rose`, `$stable`,
`$onehot`, `$countones`, …) live in the tool-agnostic reference: **`knowledge/shared/sva-reference.md`**.
This module covers the *formal-friendly methodology* for using them.

## Tool-Specific Notes

### JasperGold
- `$isunknown` support requires the `-enable_sva_isunknown` switch. [JG-specific]
- The QRG points to the JasperGold command reference for SVA-related switches.

### VC Formal
> 📝 GAP — No VC Formal property-writing notes in the current source. To be added.

## Command Reference

Directives used in this module (full operator/function/clocking syntax is in `knowledge/shared/sva-reference.md`):

| Command / Syntax | Purpose | Tool |
|---|---|---|
| `assert property (expr)` | require the property holds under all circumstances | Both |
| `assume property (expr)` | constrain DUT inputs to specified behavior | Both |
| `cover sequence (seq)` / `cover property (expr)` | demonstrate a witness of how a sequence completes | Both |
| `disable iff` / `default disable iff` | drop outstanding obligations (reset) | Both |
| `s_eventually` | unbounded liveness | Both |
| `-enable_sva_isunknown` | enable `$isunknown` support | JG |

> 📝 GAP — The single source is a 2-page quick-reference. Topics planned for this module but **not yet covered by any extraction**: safety vs liveness classification methodology, fairness properties, multi-clock/CDC property patterns, property libraries / reuse strategy, vacuity detection workflow, and design-intent-driven property development. Add sources (user guides, app notes, training) to fill these.

## Further Reading

- For complexity reduction (auxiliary code, keeping N small, abstraction): see `complexity-management.md`
- For proof engine selection, especially liveness: see `engine-tuning.md`
- For SVA operator/function/clocking syntax reference: see `knowledge/shared/sva-reference.md`
