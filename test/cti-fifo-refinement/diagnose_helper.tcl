if {[catch {
    source proof_utils.tcl
    source helpers.tcl
    add_helpers 0
    set controls [prove_control_helpers 0]
    foreach h $controls {
        require_proven $h
        assert -set_helper $h
    }
    set target H_mem_watch_live
    prove -property $target -sst 2 -engine_mode B -time_limit 10s
    dump_prop $target
    set tid [get_property_info $target -list trace_id]
    if {$tid eq ""} {error "No SST trace; inspect this version's proof log"}
    set metadata [get_trace_info $tid]
    puts "SST_METADATA $metadata"
    array set meta $metadata
    if {![info exists meta(tag)] || $meta(tag) ne "SST"} {error "Trace is not tagged SST"}
    visualize -violation -sst -property $target -trace_id $tid -new_window diag
    visualize -save -vcd evidence/helper_sst.vcd -force -window diag
    report -file evidence/helper_sst.txt -detailed
} message]} {puts "RUN_ERROR $message"; puts $::errorInfo; exit 1}
exit 0
