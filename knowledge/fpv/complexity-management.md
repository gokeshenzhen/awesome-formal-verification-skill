# Complexity Management for Formal Property Verification

> **Mature** — Generated from 50 source documents, 2026-03-29

## Overview

Complexity management is the core discipline that determines whether formal proofs converge or time out. This module covers abstraction techniques (counter, memory, initial-value, synchronizer), cone-cutting with `stopat`, free-variable/NDC methods, proof decomposition (AG, CAG, helpers), profiler-guided workflows, and under/over-constraint management. Consult this module whenever a property is bounded or inconclusive after reasonable engine time.

## Quick Decision Tree

```
Property not converging?
├─ Have you profiled? → No → Run formal_profiler, see "Profiler-Guided Stopat Mining"
├─ Large counters in cone? → Yes → See "Counter Abstraction"
├─ Large memories in cone? → Yes → See "Memory Abstraction"
├─ X-state / reset issues? → Yes → See "Initial Value Abstraction (IVA)"
├─ Multi-instance / symmetric? → Yes → See "Free Variables / NDC"
├─ Single property too hard? → Yes → See "Proof Decomposition (AG/CAG)"
├─ Need lemma scaffolding? → Yes → See "Helper Assertions"
├─ Many irrelevant signals? → Yes → See "Stopat / Cone Cutting"
├─ Synchronizers in path? → Yes → See "Synchronizer Abstraction"
├─ Design too large overall? → Yes → See "Parameter Reduction"
└─ False CEX / missed bugs? → Yes → See "Under/Over-Constraint Management"
```

## Core Rules

1. **Profile before abstracting.** Use `formal_profiler` to identify zero-effort signals; blind abstraction risks cutting proof-relevant state.
2. **Always pair `abstract -init_value` with `assume -bound 1`.** Freeing initial state without re-constraining legal invariants causes spurious counterexamples.
3. **Use explicit `-values` for signoff.** `abstract -counter -find` is exploratory; commit to explicit milestone values in production scripts.
4. **Include reset value `0` in counter abstraction values.** Omitting it breaks the reset-to-milestone path.
5. **`stopat` alone is never sufficient.** Always add legality assumptions (`assume -constant`, `assume -bound 1`, or transition constraints) after cutting a signal.
6. **Prove helpers before using them.** `assert -set_helper` on an unproven assertion is unsound; always `prove -property helper` first.
7. **Separate model setup from proof decomposition.** Create a `SETUP` task first, then derive `ROOT` from it.
8. **Sound results live on ROOT, not on local AG/CAG nodes.** Only the propagated ROOT status is the verified result.
9. **Detect overconstraint actively.** Use `check_assumptions -dead_end` and reachability covers to ensure assumptions don't block real behavior.
10. **Persist reductions to files.** Write generated `stopat` decks to `.tcl` files via `eju_list_to_file` so they survive across sessions.

## Pattern Catalog

### Counter Abstraction (Automatic)

**When to use**: Property cone contains counters with large bit-widths (>16 bits) where only specific threshold values matter.

**Template**:
```tcl
# Step 1: Discovery (exploratory only)
abstract -counter -find

# Step 2: Explicit milestone abstraction (signoff)
abstract -counter <sig> -values 0 <threshold1> <threshold2> ...

# Optional: disable during reset
abstract -counter <sig> -values 0 <v1> <v2> -disable_condition <rst>
```

**Example**:
```tcl
# 32-bit counter with two milestone comparisons at (2^23)-19346 and (2^28)-28311
abstract -counter cntr -values 0 8369262 268407145
prove -all   ;# converges quickly vs. timeout on direct proof
```

**Gotchas**:
- Values come directly from RTL compare expressions — compute carefully
- Abstraction is only valid when properties observe milestone-driven events, not intermediate counts
- `complexity_manager` may miss rare threshold values; verify with explicit `-values`

### Counter Abstraction (Manual 4-Step)

**When to use**: Automatic abstraction insufficient; need custom abstract state encoding for non-standard counter behavior.

**Template**:
```systemverilog
// Step 1: Abstract state model
module CntModel (input clk);
  reg [1:0] CntState; wire [1:0] NextCntState;
  always @(posedge clk) CntState <= NextCntState;
endmodule
```
```tcl
# Step 2: Repository connect
analyze -repository 0 CntModel.v
elaborate -repository 0
connect CntModel i_CntModel -repository 0

# Step 3: Transition assumptions (one per valid transition)
assume {!inc => NextCntState == CntState}
assume {inc && CntState == 1 => NextCntState == 3}
assume {inc && CntState == 2 => NextCntState == 1}
assume {inc && CntState == 3 => NextCntState == 2 || NextCntState == 3}

# Step 4: Cut RTL counter, re-drive from abstract state
stopat cnt
assume {CntState == 1 => cnt == MaxCount}
assume {CntState == 2 => cnt == MaxCount - 1}
assume {CntState == 3 => cnt < MaxCount - 1}
assume {CntState != 0}   ;# block illegal encoding
```

**Gotchas**:
- One abstract state per distinct threshold/range — don't merge proof-relevant values
- Always add `CntState != 0` (or equivalent) to block illegal encodings
- Try automatic `abstract -counter` first; go manual only when insufficient

### Initial Value Abstraction (IVA)

**When to use**: Spurious counterexamples from unknown initial states; X-state explosion at reset.

**Template**:
```tcl
# Free initial value, then re-constrain with bound-1 assumption
abstract -init_value <sig>
assume -bound 1 "<sig> == <legal_init>"

# For reset pin abstraction
abstract -reset_value <sig>

# Convenience proc
proc apply_counter_iva {sig} {
  abstract -init_value $sig
  assume -bound 1 "$sig == 0"
}
```

**Example** (linked-list allocator):
```tcl
abstract -init list_ctrl.wrptr
assume -name wrptr_start -bound 1 {list_ctrl.wrptr <= list_ctrl.SIZE}

for {set idx 0} {$idx < $SIZE} {incr idx} {
  abstract -init "list_ctrl.mem[$idx]"
  assume -name "mem_init_$idx" -bound 1 \
    "list_ctrl.wrptr > $idx |-> list_ctrl.mem[$idx] == $idx"
}
```

**Gotchas**:
- `abstract -init_value` without any `-bound 1` constraint → proof explores impossible initial states
- Both `-init_value` and `-reset_value` may be needed: init covers cycle 0, reset covers the reset pin
- Over-abstracting removes proof-relevant state; use `stopat -remove <sig>` to restore

### Free Variables / NDC (Non-Deterministic Choice)

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

### Memory Abstraction

**When to use**: Large SRAM/memory arrays dominate the proof cone; only a few addresses are proof-relevant.

**Template** (black-box + abstract reconnect):
```tcl
# Black-box the memory instance
elaborate -bbox_i <mem_instance>

# Analyze abstract model and reconnect outputs
analyze -sv09 <mem_abs>.sv
assume -name connect_rd0 {<inst>.mem.rd0data == <inst>.<abs>.rd0data}
assume -name connect_rd1 {<inst>.mem.rd1data == <inst>.<abs>.rd1data}
```

**Template** (symbolic slot abstraction):
```systemverilog
parameter ABS_NUM = 4;
logic [DATA_WIDTH-1:0] mem_content[ABS_NUM-1:0];
logic [ADDR_WIDTH-1:0] active_addr[ABS_NUM-1:0];
assume property (##1 $stable(active_addr));
// valid_num = index where addr matches active_addr[i]
// On read: dout = (match found) ? mem_content[match_idx] : garbage_val
// garbage_val is intentionally undriven — do not constrain it
```

**Example** (coloring memory — stores symbol flag, not full payload):
```systemverilog
wire [DATA_W-1:0] symbol_ndc;
wire symbol_detected = (symbol_ndc == wr0data[ADDR_W+2+:DATA_W]);
bit [SIZE-1:0][ADDR_W+2:0] mem, mem_nx;
always_comb begin
  if (wr0) mem_nx[wr0addr] = {symbol_detected, wr0data[ADDR_W+1:0]};
end
ASM_symbol_on_rd0: assume property (
  $past(rd0 & mem_nx[rd0addr][ADDR_W+2]) == (rd0data[ADDR_W+2+:DATA_W] == symbol_ndc));
```

**Gotchas**:
- `-bbox_i` without reconnecting abstract model → outputs fully unconstrained
- `garbage_val` is intentionally free; guard assertions with `!garbage_op`
- Coordinate `symbol_ndc` between abstract memory and scoreboard: `assume {abs.symbol_ndc == sb.symbol}`
- `-disable_auto_bbox` + `-bbox_i inst`: disable global auto-boxing, then box one explicit instance

### Profiler-Guided Stopat Mining

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

### Proof Decomposition (AG / CAG)

**When to use**: Single property too complex; can be decomposed via helper lemmas or compositional reasoning.

**Template** (Assume-Guarantee):
```tcl
task -create SETUP -copy_assert -set
# Build helpers (e.g., virtual_net + assert)
proof_structure -init ROOT -from SETUP -copy_all
proof_structure -create assume_guarantee \
  -from ROOT -op_name AG1 -imp_name {AG1.G AG1.A} \
  -property [list helper1 target_prop]
prove -property AG1.A::target_prop    ;# prove target assuming helper
prove -property AG1.G::helper1        ;# prove helper independently
```

**Template** (Compositional Assume-Guarantee):
```tcl
proof_structure -init ROOT -from SETUP \
  -copy_assumes -copy_abstractions all -copy_stopats
proof_structure -create compositional_assume_guarantee \
  -from ROOT -op_name CAG -property [list prop1 prop2 ...]
prove -task {CAG.0} -assert -engine {N} -time_limit 100s
prove -task {CAG.1} -assert -engine {N} -time_limit 100s
# Check ROOT status — that is the sound result
```

**Template** (Multi-Stage AG for scaling):
```tcl
set ML_helpers_2:5 "helper2 helper3 helper4 helper5"
set ML_helpers_1:5 "helper1 ${ML_helpers_2:5}"
proof_structure -init ROOT -from SETUP -copy_all
# Stage 1: prove helpers 2:5
proof_structure -create assume_guarantee -from ROOT \
  -op_name AG_stage1 -property [list ${ML_helpers_2:5}]
# Stage 2: use helpers 1:5 to prove target
proof_structure -create assume_guarantee -from ROOT \
  -op_name AG_stage2 -property [list ${ML_helpers_1:5} addN.target]
```

**Runtime data** (adderN benchmark):
| N | Direct proof | With AG decomposition |
|---|---|---|
| 8 | ~1 min | — |
| 12 | ~50 min | ~90 s |
| 16 | ~3.6 h | ~11 min |

**Gotchas**:
- CAG supports embedded SVA only (no bind-style assertions)
- `-copy_abstractions all` is required — env constraints must propagate to CAG nodes
- `::jasper::psu::prove_all ROOT` auto-proves all obligations in the proof tree
- Local CAG node results are NOT sound; only propagated ROOT is valid for signoff

### Helper Assertions (Lemmas)

**When to use**: Target property needs intermediate invariants to converge.

**Template**:
```tcl
assert -helper -name helper1 {<invariant_expression>}
prove -property helper1
assert -set_helper helper1
prove -property target_prop -with_helpers
```

**Example** (loop-generated FIFO tag helpers):
```tcl
for {set i 0} {$i < 16} {incr i} {
  assert -helper -name help_tag_$i \
    "(id_fifo.fifo_valid\[$i\] && id_fifo.fifo_out\[$i\]\[0\]) |-> \
     (id_fifo.fifo_out\[$i\]\[75:68\] == v_top.ID)"
}
prove -property {top.v_top.ast_has_same_id_on_ID} -time_limit 2m -with_helpers
```

**Gotchas**:
- `-with_helpers` is **required** — omitting it ignores declared helpers
- `assert -mark_proven helper`: injects externally verified result (soundness depends on external proof)
- Loop-generated helpers must escape `[` and `]` in Tcl strings

### State Space Tunneling (SST)

**When to use**: Proof stalls in irrelevant initialization cycles before reaching interesting states.

**Template**:
```tcl
prove -property {target} -sst <N>    ;# N = tunnel depth
set_sst_default_trace_length 8
```

**Gotchas**: Set `-sst N` based on design init depth; too shallow is ineffective.

### Synchronizer Abstraction

**When to use**: Clock-domain-crossing synchronizers add unnecessary depth to the proof cone.

**Template**:
```tcl
elaborate -bbox_m pp_sync -bbox_m pp_sync_pulse
foreach i $pp_sync_bbox {
  assume "$i.in == $i.out" -name sync_abstraction_$i
}
foreach i $pp_sync_pulse_bbox {
  assume "$i.busy |-> $i.in"     -name "sync_pulse_valid_$i"
  assume "|$i.busy |=> ~$i.busy" -name "sync_pulse_$i"
}
```

**Gotchas**: `-bbox_m` without behavioral re-contract leaves all outputs unconstrained.

### Parameter Reduction

**When to use**: Design parameters make the state space too large for formal.

**Template**:
```tcl
elaborate -top <module> -parameter DATA_MEM_SIZE 16
elaborate -top <module> -parameter M1_ADDR_MAX 64
```

**Gotchas**: Reduced parameters may hide size-dependent bugs; document the reduction.

### Clock Ratio Management

**When to use**: Multi-clock designs where async proofs need robustness across static ratios.

**Template**:
```tcl
clock clk_a -from 1 -to 2 -both_edges
clock clk_b -from 1 -to 2 -both_edges
```

**Gotchas**:
- Start with fixed ratios; widen to ranges only after fixed-factor bugs are resolved
- `-both_edges` + range → search space expands over both factor and phase
- Does NOT model dynamic frequency/phase changes between cycles

## Anti-Pattern Reference

| Anti-Pattern | Why It Fails | Correct Alternative |
|---|---|---|
| `reset -none` | X-state explosion, spurious CEX | `reset rst` with correct polarity |
| `abstract -counter -find` in signoff | Exploratory; may miss thresholds | `abstract -counter sig -values 0 v1 v2` |
| `stopat` without re-constraining | Signal fully unconstrained | `assume -constant` + legality bounds |
| `abstract -init_value` without `assume -bound 1` | Explores impossible initial states | Always pair with `assume -bound 1` |
| Unproven helper as `-set_helper` | Unsound lemma | `prove -property helper` first |
| CAG local node result as signoff | Not sound | Use propagated ROOT result only |
| Overconstraints on baseline task | Masks real bugs | Clone: `task -create oc -source_task baseline -copy_all` |
| Proving all IDs simultaneously | State explosion | One stable symbolic `chosen_id` |
| `-bbox_i` without abstract reconnect | Outputs unconstrained | Add `assume` tying outputs |
| Wide clock ranges by default | Exponential complexity | Fixed-factor first; ranges last |
| Profiling without isolating property | Misleading effort scores | `assert -disable *; assert -enable <target>` |

## Under/Over-Constraint Management

### Underconstraint (false alarms)
- **Symptom**: CEX shows behavior impossible in real design
- **Fix**: `reset -non_resettable_regs 0`; add `assume -reset`; apply IVA pattern
- **Diagnosis**: Add history witness signals to track impossible state sequences in CEX

### Overconstraint (missed bugs)
- **Symptom**: Properties pass but covers are unreachable
- **Detection**: `check_assumptions -dead_end [-minimize]`
- **Practice**: Clone tasks for experiments:
```tcl
task -create oc_test -source_task baseline -copy_all -set
assume -name oc_constraint {<expr>}
```
- **Recovery**: `get_needed_assumptions -property <prop> -engine_mode {B4 I N}`

> 📝 GAP: No extraction covers automated regression-level overconstraint detection across property suites.

## Tool-Specific Notes

### JasperGold

- `complexity_manager [-property <prop>]`: auto-selects abstractions; manual override if thresholds missed
- `formal_profiler`: mine zero-effort signals for safe `stopat` candidates
- `get_design_info -list fsm|counter|array -no_aggregate -silent`: enumerate design structures
- `visualize -relevant_logic <prop> -configuration undriven_only`: inspect proof cone
- `proof_structure`: AG, CAG, partition, hard_case_split decomposition
- `set_proofmaster on; set_proofmaster_dir <dir>`: persist proof cache across sessions
- `hunt -config -mode cycle_swarm|state_swarm`: advanced cover/proof search
- `set_engineL_overconstraining_factor 0.3`: tune engine-L aggressiveness
- `set_prove_clock_optimization on`: reduce multi-clock scheduling overhead
> 🔧 VERSION-SENSITIVE: CAG and `proof_structure` commands documented for JG 2021.06FCS and 2023.03FCS. Syntax may differ in earlier versions.

### VC Formal

> 📝 GAP: No source extractions cover VC Formal complexity management. To be added.

## Command Reference

| Command | Purpose | Tool |
|---|---|---|
| `abstract -counter <sig> -values <v0> <v1>` | Milestone counter abstraction | JG |
| `abstract -counter -find` | Discovery pass for abstractable counters | JG |
| `abstract -init_value <sig>` | Free initial value of signal | JG |
| `abstract -reset_value <sig>` | Free reset value of signal | JG |
| `stopat <signal>` | Cut signal from proof cone | JG |
| `stopat -remove <signal>` | Restore previously cut signal | JG |
| `stopat -env <signal>` | Cut env-side cone | JG |
| `assume -bound 1 {<cond>}` | Constrain initial state only | JG |
| `assume -constant <sig>` | Make signal time-invariant (spatial NDC) | JG |
| `complexity_manager -property <prop>` | Auto-select abstractions | JG |
| `formal_profiler -show <p> -list bound` | List profiled bounds | JG |
| `formal_profiler -report -bound $c -signal $s` | Signal effort at bound | JG |
| `get_design_info -list fsm\|counter\|array` | Enumerate design structures | JG |
| `elaborate -bbox_i <inst>` | Black-box specific instance | JG |
| `elaborate -bbox_m <module>` | Black-box all instances of module | JG |
| `elaborate -parameter <name> <value>` | Override design parameter | JG |
| `proof_structure -init ROOT` | Initialize proof tree | JG |
| `proof_structure -create assume_guarantee` | AG decomposition | JG |
| `proof_structure -create compositional_assume_guarantee` | CAG decomposition | JG |
| `proof_structure -create partition` | Partition properties | JG |
| `assert -helper -name <n> {<expr>}` | Declare helper lemma | JG |
| `assert -set_helper <name>` | Activate proven helper | JG |
| `prove -property <p> -with_helpers` | Use helpers in proof | JG |
| `prove -property <p> -sst <N>` | State space tunneling | JG |
| `check_assumptions -dead_end` | Detect overconstraint | JG |
| `get_needed_assumptions -property <prop>` | Find minimal assumption set | JG |
| `reset -non_resettable_regs 0` | Suppress non-resettable warnings | JG |
| `set_word_level_reduction on` | Enable word-level reasoning | JG |
| `set_prove_advanced_simplification on` | Advanced simplification | JG |
| `set_prove_clock_optimization on` | Multi-clock optimization | JG |
| `set_engine_threads <N>` | Parallel engine threads | JG |

## Further Reading

- For engine selection and tuning strategies: see `engine-tuning.md`
- For SVA property writing patterns: see `property-writing.md`
- For reset and clock setup: see `environment-setup.md`
- For coverage closure: see `coverage.md`
