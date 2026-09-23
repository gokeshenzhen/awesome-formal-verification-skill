# Run the entry-point scripts from this directory, in separate Jasper sessions.
source neutral/setup.tcl
file mkdir evidence

proc dump_prop {p} {
    puts "RESULT $p [get_property_info $p -list {status validity_status min_length max_length engine time trace_id}]"
}

proc require_proven {p} {
    lassign [get_property_info $p -list {status validity_status min_length max_length}] s v lo hi
    if {$s ne "proven" || $v ne "proven" || $lo ne "infinite" || $hi ne "infinite"} {
        error "Unclosed obligation: $p ($s $v $lo $hi)"
    }
}

proc prove_one {p support limit} {
    foreach h $support {
        if {$h eq $p} {error "Self-support: $p"}
        require_proven $h
        puts "PROVEN_SUPPORT $p $h"
    }
    # Only previously proved assertions may support a new obligation.
    set_proven_directive true
    set selected [linsert $support 0 $p]
    puts "PROOF_REQUEST $selected limit=$limit engines=H,AM,N"
    prove -property $selected -engine_mode {H AM N} \
        -per_property_time_limit_factor 0 -per_property_time_limit $limit -time_limit $limit
    dump_prop $p
}

proc prove_checked {p support limit} {
    prove_one $p $support $limit
    require_proven $p
}
