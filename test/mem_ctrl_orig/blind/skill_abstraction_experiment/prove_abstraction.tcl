# prove_abstraction.tcl
# ─────────────────────────────────────────────────────────────────────────────
# DISCLOSED TRUSTED memory abstraction for mem_ctrl_top.u_mem.mem_works_ndc.
# Top-level, reproducible version of the skill-guided blind run (originally
# captured under run_20260624_185303/prove_mem_abstraction_v3.tcl).
#
# Method (knowledge/fpv/complexity-management/abstraction.md "Memory Abstraction"):
#   - black-box ONLY the array instance  u_mem.m1  via -bbox_i (removes the
#     512x32 = 16,384 mem_content flops from the proof cone)
#   - mem_slot_bind.sv binds a single-slot tracker (mem_slot_abs u_abs) keyed to
#     the property's own symbolic ndc_addr
#   - a reconnect `assume` ties the black-boxed m1.dout to the tracked word
#
# Benchmark RTL (simple_mem_design.sv, mem_ctrl_top.sv) is analyzed UNCHANGED.
# mem_slot_bind.sv is a DISCLOSED abstraction helper, NOT original RTL.
# Signoff class: DISCLOSED TRUSTED-ABSTRACTION RESULT (not raw-RTL signoff).
# ─────────────────────────────────────────────────────────────────────────────

set bench_dir $::env(BENCH_DIR)
set exp_dir   $::env(EXP_DIR)
set run_dir   $::env(RUN_DIR)

clear -all

## 1. ANALYZE — benchmark RTL unchanged + disclosed abstraction helper
analyze -sv09 "$bench_dir/simple_mem_design.sv"
analyze -sv09 "$bench_dir/mem_ctrl_top.sv"
analyze -sv09 "$exp_dir/mem_slot_bind.sv"      ;# NOT original RTL — disclosed helper

## 2. ELABORATE — black-box ONLY the array instance (u_mem.m1 path is rel. to top)
elaborate -top mem_ctrl_top -bbox_i {u_mem.m1}

puts "=== Design info after bbox (mem_content array should be gone) ==="
get_design_info -list flop
get_design_info -list bbox_inst

## 3. CLOCK & RESET
clock clk
reset -expression {rst}

## 4. MEMORY CONTRACT — disclosed trusted reconnect of the black-boxed read
#  rd_ndc_q : prev cycle read at ndc_addr   (registered inside u_abs)
#  tracked_q: last value written to ndc_addr, 1-cycle delayed (registered)
assume -name mem_contract \
  {u_mem.u_abs.rd_ndc_q |-> u_mem.m1.dout == u_mem.u_abs.tracked_q}

## 5. NON-VACUITY — cover that the target's antecedent can actually fire
cover -name precond_cover \
  {u_mem.symbol_write ##1 (!u_mem.addr_write)[*1:$] ##1 u_mem.addr_read}

## 6. SANITY
sanity_check
check_assumptions -dead_end

## 7. PROVE
set_prove_time_limit 30m
set_prove_per_property_time_limit 20m
prove -all

## 8. REPORT
report -file "$run_dir/prove_summary.rpt"  -summary
report -file "$run_dir/prove_detailed.rpt" -detailed
puts "=== DONE — summary in $run_dir/prove_summary.rpt ==="

exit
