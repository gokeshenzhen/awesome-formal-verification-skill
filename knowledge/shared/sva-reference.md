# SVA Reference

> 🔬 **from-docs** — Generated from Cadence JasperGold documentation, 2026-06-14. Needs field validation.

Tool-agnostic SystemVerilog Assertions (SVA) syntax and semantics reference — the operators, delays, functions, and declaration forms themselves. For **how to write properties for formal** (decision tree, patterns, the formal-friendly subset, anti-patterns), see `knowledge/fpv/property-writing.md`.

## Sequence & Property Declaration

```systemverilog
sequence identifier [ argument_list ];
  sequence_expr ;
endsequence

property identifier [ argument_list ];
  [ clock_expr ] [ disable_clause ]
  property_expr ;
endproperty
```
Examples:
```systemverilog
sequence SEQ1;            A ##1 B ##1 C;            endsequence
sequence SEQ2(LEN, SIG);  D ##1 E[*LEN] ##1 SIG;    endsequence
property  P1 (R, S, T);
  @(posedge clk) disable iff (!rst_n)
    A |=> R ##1 S && T;
endproperty
```
A one-cycle sequence is identical to a Boolean expression. Prefer defining/inferring a sequence's clock at instantiation, not at declaration.

## Cycle Delays

- `##N` — fixed delay of N cycles.
- `##[N:M]` — delay range; `M` may be `$` (infinity); requires `M >= N`; both may be 0.
- `##[0:$]` / `##[+]` — unbounded / one-or-more.
```systemverilog
P8_NXTCYC: assert property( A |=> B ##[0:$] C );
P8_SMECYC: assert property( A |=> ##3 C );
```

## Repetition

| Form | Meaning |
|---|---|
| `seq[*N]`, `seq[*N:M]` | consecutive repetition |
| `seq[->N]` | GoTo (non-consecutive, N-th match) |
| `seq[=N]` | non-consecutive repetition |

> `[->N]` and `[=N]` create unbounded-length sequences; keep `[*N]` depth small. See `property-writing.md` for the formal-friendly guidance.

## Implication Operators

- `seq |-> prop` (**overlapped**): if `seq` completes, `prop` starts the **same** cycle and must complete; also holds if `seq` never completes.
- `seq |=> prop` (**non-overlapped**): if `seq` completes, `prop` starts the **next** cycle; equivalent to `A ##1 B |-> …` (i.e. `A |=> B` ≡ `A ##1 B |-> …`).
```systemverilog
P6: assert property ( A ##1 B |-> C ##1 D );   // C aligns with B
P7: assert property ( A ##1 B |=> C ##1 D );   // C one cycle after B
```

## Verification Directives

A property declaration alone checks nothing; a directive tells the tool to act.

| Directive | Meaning |
|---|---|
| `label : assert property (expr)` | require the property holds under all conditions |
| `label : assume property (expr)` | constrain inputs to the specified behavior (a.k.a. constraint) |
| `label : cover property (expr)` / `cover sequence (seq)` | demonstrate one witness of how a sequence completes |

```systemverilog
P2 : assert property ( @(posedge clk) A |-> B );
P4 : assume property ( req && !gnt |=> req );
C1 : cover  sequence ( full ##[+] empty );
```
For `cover`, the body should be a pure sequence (no `|->` / `|=>`).

## Disabling Properties

```systemverilog
disable iff (boolean_expr)            // per-property: drop outstanding obligations when true
default disable iff (boolean_expr);   // scope-wide default for properties without an explicit one
```
An explicit `disable iff` overrides the `default`. Both act **asynchronously** — independent of the property's clock. For synchronous abort see `sync_accept_on` / `sync_reject_on` (LRM).

## Clocking

```systemverilog
default clocking MYCLK @(posedge clk2); endclocking
```
- Clock sources, precedence order: explicit clock at instantiation **or** declaration (explicit always wins) > `default clocking` for the scope.
- A sequence with no explicit clock inherits its parent property's clock.
- Only one `default clocking` per scope; applies to that scope only. SVA properties cannot be unclocked.

## Sampled-Value & System Functions

"Cycle" = the property's clock — not ns/ps, timescale, or hardware clock.

| Function | Returns |
|---|---|
| `$past(expr, N)` | value of `expr` N cycles ago (N defaults to 1) |
| `$rose(expr)` | TRUE if expr is TRUE now and was FALSE last cycle |
| `$fell(expr)` | TRUE if expr is FALSE now and was TRUE last cycle |
| `$stable(expr)` | TRUE if expr unchanged from last cycle |
| `$onehot(expr)` | TRUE if exactly one bit is 1 |
| `$onehot0(expr)` | TRUE if at most one bit is 1 |
| `$isunknown(expr)` | TRUE if any bit is X or Z |
| `$countones(expr)` | integer count of 1-bits |

```systemverilog
P12 : assert property( req && !gnt |=> $stable(addr) );
P13 : assert property( $onehot(GNT_VEC) );
P14A: assert property( !RDY |=> DAT == $past(DAT) );
```

## Liveness

- `s_eventually expr` — strong unbounded liveness ("eventually true").
```systemverilog
property P1A; REQ |=> s_eventually GNT; endproperty
```

## Further Reading
- For formal-friendly property-writing methodology, patterns, and anti-patterns: see `knowledge/fpv/property-writing.md`
- For Tcl that drives these into a tool: see `knowledge/shared/tcl-common.md`
- Authoritative spec: IEEE 1800-2017 LRM, "Assertions" chapter.
