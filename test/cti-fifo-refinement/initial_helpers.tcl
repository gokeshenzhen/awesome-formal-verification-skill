if {[catch {
    source proof_utils.tcl
    source helpers.tcl
    add_helpers 0
    set controls [prove_control_helpers 0]
    prove_one H_mem_watch_live $controls 20s
    # This stage records the stalled candidate; do not use it to prove P0.
    puts "INITIAL_CANDIDATE [get_property_info H_mem_watch_live -list {status validity_status}]"
    report -file evidence/initial_helpers.txt -detailed
} message]} {puts "RUN_ERROR $message"; puts $::errorInfo; exit 1}
exit 0
