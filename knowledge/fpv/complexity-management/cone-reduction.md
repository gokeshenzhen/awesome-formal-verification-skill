# Complexity: Cone Reduction (Cut & Free Signals)

> Leaf of `complexity-management.md`. Shrink the cone of influence by cutting signals out of it (`stopat`/cutpoints) or by replacing whole value spaces with one symbolic representative (free variables / NDC). The cardinal rule: **every cut must be paired with a legality constraint**, or the proof explores impossible behavior.

## Free Variables / NDC (Non-Deterministic Choice)

**When to use**: Prove a property for all IDs, threads, addresses, or data values by picking one symbolic representative.

**Template** (Spatial NDC — stable):
```systemverilog
logic [WIDTH-1:0] chosen_id;
assume property ($stable(chosen_id));
// Track only the chosen representative
assign match = (in_valid && in_id == chosen_id);
```

**Template** (Temporal NDC — changes each cycle):
```tcl
stopat <signal>                    ;# cut logic cone
# signal is now unconstrained each cycle; add legality constraints
assume {<signal> < MAX_LEGAL}
```

**Example** (coloring/signature scoreboard):
```systemverilog
logic [DATA_W-1:0] symbol;
assume property ($stable(symbol));
logic injected_once, injected_twice;
always @(posedge clk or negedge rstn) begin
  if (~rstn) begin injected_once <= 0; injected_twice <= 0; end
  else if (ig_payload_valid && curr_payload == symbol) begin
    injected_once <= 1'b1; injected_twice <= injected_once;
  end
end
assume property (ig_payload_valid && injected_once && !injected_twice
                 |-> curr_payload == symbol);
assume property (ig_payload_valid && injected_twice
                 |-> curr_payload != symbol);
typedef enum logic [1:0] {IDLE, FIRST, DONE, ERROR} state_t;
ast_coloring_data_integrity: assert property (state != ERROR);
```

**Gotchas**:
- `stopat` alone without re-constraining → unconstrained nonsense values
- Forgetting `$stable` on spatial NDC → free variable changes mid-proof
- Coloring proves universal coverage via one representative — no need to iterate all values

## Configuration Cutpoints with Legality Assumptions

**When to use**: Configuration/control logic dominates the cone of influence. The config is written once (e.g. at init) and then held stable, but its generation logic is large.

`stopat` is the JasperGold cutpoint mechanism — it removes a signal's driver so the signal becomes a free input. A **cutpoint on a configuration signal** drops the whole config-generation cone; you then re-add only the legality of the config as assumptions, so the proof runs over *legal* configurations without traversing the config logic.

**Template**:
```tcl
# 1. Cutpoint the internal configuration signals (drop their generation logic)
stopat <cfg_sig_a> <cfg_sig_b> ...

# 2. Re-impose legality: convert the design's config-validity checks into assumptions
#    so only legal configurations are explored.
assume -name cfg_legal_a {<cfg_validity_expr_a>}
assume -name cfg_legal_b {<cfg_validity_expr_b>}
# setup_ndc is the helper that sets up a cut signal as a legally-constrained
# non-deterministic choice (pairs the cut with its validity constraint).
setup_ndc <cfg_sig> -legal {<validity_expr>}
```

**Key insight**: convert configuration-validity *checkers* already in the design into assumptions — the proof then operates over legal config states only, instead of re-deriving them through the (now cut) config logic.

**Gotchas**:
- ❗ Cutpointing config signals **without** constraining legal values → the proof explores impossible/invalid configurations → spurious counterexamples. Always pair the cutpoint with legality assumptions (via `setup_ndc` or explicit `assume`).
- A cutpoint is only sound when the cut block does not itself need verification in this task — remove it structurally, then remodel only the behavior the proof needs.
- ⚠️ NEEDS VALIDATION: `setup_ndc` is referenced in the source labs but lightly documented; confirm exact switches against your JasperGold version.

## Profiler-Guided Stopat Mining

**When to use**: After initial profiling shows many zero-effort signals that can be safely cut.

**Template**:
```tcl
# Isolate target property first
assert -disable *; cover -disable *; assert -enable <target>

# Mine zero-effort signals
set bounds [formal_profiler -show [lindex [formal_profiler -list] end] -list bound]
set fsm_list [get_design_info -list fsm -silent]
set cnt_list [get_design_info -list counter -silent]
set ary_list [get_design_info -list array -no_aggregate -silent]

foreach s $clist {
  set zero_effort 1
  foreach c [lindex $bounds 0] {
    set e [lindex [formal_profiler -report -bound $c -signal $s] 1]
    if {$e != "0.00"} { set zero_effort 0 }
  }
  if {$zero_effort == 1} {
    lappend zlist_cmd_list "catch {stopat {$s}}"
  }
}
eju_list_to_file $zlist_cmd_list "mine_zero_signals_stopat_output.tcl"
source mine_zero_signals_stopat_output.tcl

# Restore proof-relevant state
stopat -remove <proof_relevant_signal>*
```

**Gotchas**:
- `catch {}` wrapper is essential — some signals may not be stoppable
- Always selectively restore proof-relevant signals after bulk stopat
- Mining without isolating to one property first gives misleading effort scores
- Generated files can be large (10K+ lines); persist and `source` them

## Parameter Reduction

**When to use**: Design parameters make the state space too large for formal.

**Template**:
```tcl
elaborate -top <module> -parameter DATA_MEM_SIZE 16
elaborate -top <module> -parameter M1_ADDR_MAX 64
```

**Gotchas**: Reduced parameters may hide size-dependent bugs; document the reduction.

## See Also
- Replacing a structure with an abstract model (counter/memory/sync): `abstraction.md`
- Index, decision tree, core rules, anti-patterns: `../complexity-management.md`
