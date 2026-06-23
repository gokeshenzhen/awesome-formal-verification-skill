# Complexity: Abstraction Techniques

> Leaf of `complexity-management.md`. Replace a large/deep structure with a smaller abstract model that preserves only proof-relevant behavior. Covers counter, initial-value, memory, and synchronizer abstraction.

## Counter Abstraction (Automatic)

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

## Counter Abstraction (Manual 4-Step)

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

## Initial Value Abstraction (IVA)

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

## Memory Abstraction

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

## Synchronizer Abstraction

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

## See Also
- Cutting signals out of the cone (stopat, cutpoints, free variables): `cone-reduction.md`
- Index, decision tree, core rules, anti-patterns: `../complexity-management.md`
