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

**Trigger checklist — raw memory proof has stalled.** Escalate to abstraction (stop re-racing engines and looping `prove -all`) when *all* of these hold:
- reset/`get_design_info` analysis shows **thousands of memory flops** dominating the flop count (e.g. a 512-entry × 32-bit array ≈ 16 K flops)
- the target is an **arbitrary-address write→read** assertion — a symbolic/`$stable` address that must hold for *all* addresses
- the property's precondition **cover is reachable** (non-vacuous) but the assertion stays `undetermined`
- **no CEX** appears after multiple engine scans / per-property time limits expire
→ black-box the array and reconnect a symbolic-slot model. Confirm the array first with `get_design_info -list array -no_aggregate -silent` or `complexity_manager -property <prop>`. A controller/wrapper property closing fast does **not** imply the inner array property will — they have different cones; an arbitrary-address array assertion is itself the canonical memory-abstraction trigger.

**Concrete recipe — black-box one inner array instance, reconnect a single symbolic slot.**
Use when an *internal* arbitrary-address property (inside the memory wrapper) reads a concrete array instance and the original hierarchy must be preserved (no DUT rewrite). Keep the original top elaborated; box only the array *instance*; track only the property's own symbolic address `<ndc_addr>` (the `$stable` address the assertion is written against).

```tcl
# 1. Keep the real top; black-box ONLY the array instance by PATH (-bbox_i),
#    not by module (-bbox_m) — sibling instances stay concrete.
elaborate -top <top> -bbox_i <top>.<wrap>.<array_inst>

# 2. Bind a one-word abstract model into the wrapper, keyed to the property's
#    own symbolic NDC address. Added via a SEPARATE file — original RTL unedited.
analyze -sv09 mem_slot_abs.sv     ;# contains: bind <wrap_module> mem_slot_abs u_abs (...)

# 3. Reconnect the boxed read output to the slot — the disclosed memory contract.
#    Registered read: dout at T+1 == value last written to <ndc_addr>.
clock clk ; reset rst
assume -name mem_contract { \
  ($past(<wrap>.op)==OP_RD && $past(<wrap>.addr)==<wrap>.<ndc_addr>) \
   |-> <top>.<wrap>.<array_inst>.dout == $past(<top>.<wrap>.u_abs.tracked) }

prove -property {<arbitrary_addr_assertion>}
```
where `mem_slot_abs` tracks one word (the RAM contract projected onto `<ndc_addr>`):
```systemverilog
// mem_slot_abs.sv — NOT original RTL; a disclosed abstraction bound into the wrapper
always_ff @(posedge clk or posedge rst)
  if (rst) tracked <= '0;
  else if (op==OP_WR && addr==ndc_addr) tracked <= din;
```
This collapses the ~16 K-flop array to one data-width `tracked` register; the proof then closes in seconds. Reads of addresses other than `<ndc_addr>` are left free — sound for this property because its read antecedent only fires on `addr==<ndc_addr>`. (To dodge `$past`/enum quoting in the Tcl `assume`, register `rd_ndc_q` and `tracked_q` *inside* `mem_slot_abs` and reconnect with the plain equality `<...>.u_abs.rd_ndc_q |-> <array_inst>.dout == <...>.u_abs.tracked_q`.)

**Signoff discipline — disclosed trusted abstraction vs. raw-RTL signoff.**
- The black-box + reconnect `assume` is a **trusted memory contract**: it *assumes* the array reads back what was written at `ndc_addr`. Report it as a **disclosed trusted-abstraction proof**, never as an unqualified raw-RTL proof.
- To upgrade to full signoff, discharge the contract separately — prove the reconnect `assume` as an assertion against the real `mem_imp`, or supply an equivalence argument — then claim the embedded assertion proven on the original RTL.
- **Never rewrite the DUT module and report it as original-RTL signoff.** Replacing `simple_mem`/`mem_imp` with a smaller model proves the *replacement*, not the design. If you abstract, preserve and *reconnect* the original hierarchy (`-bbox_i <path>` + reconnect), and disclose every added `assume`/contract, the precondition covers proving non-vacuity, and which embedded assertions remain raw-unproven.

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
- Prefer `-bbox_i <instance-path>` over `-bbox_m <module>` when only one array instance must be cut — `-bbox_m` boxes *every* instance of that module
- Disclose the reconnect `assume` as a trusted contract; do not call the resulting proof an unqualified raw-RTL proof (see Signoff discipline above)

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
