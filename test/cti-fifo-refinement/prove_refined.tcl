if {[catch {
    source proof_utils.tcl
    source helpers.tcl
    add_helpers 1
    set controls [prove_control_helpers 1]
    # Same data-helper formula, engines and 20s budget as initial_helpers.tcl.
    prove_checked H_mem_watch_live $controls 20s
    prove_checked H_rd_data_mem $controls 20s
    prove_checked H_bypass_head_data [concat $controls {H_mem_watch_live}] 10s
    prove_checked H_rd_head_data [concat $controls {H_mem_watch_live H_rd_data_mem}] 15s
    set support [concat $controls {H_mem_watch_live H_rd_data_mem H_bypass_head_data H_rd_head_data}]
    prove_checked testbench.P0 $support 20s
    prove_one testbench.C_read {} 8s
    lassign [get_property_info testbench.C_read -list {status validity_status}] s v
    if {$s ne "covered" || $v ne "covered"} {error "Read cover not reached: $s $v"}
    foreach p [concat $support {testbench.P0 testbench.C_read}] {dump_prop $p}
    puts "REFINEMENT_CLOSED"
    report -file evidence/refined.txt -detailed
} message]} {puts "RUN_ERROR $message"; puts $::errorInfo; exit 1}
exit 0
