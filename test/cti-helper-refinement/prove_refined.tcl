if {[catch {
  source [file join [file dirname [info script]] setup.tcl]
  # helper_sst shows that B's next value depends on A's current relation.
  assert -helper -name h_ab {
    ((!valid[0]) || (data_a == ref_a)) &&
    ((!valid[1]) || (data_b == ref_b))
  }

  proc prove_with_support {obligation support} {
    foreach h $support {
      lassign [get_property_info $h -list {status validity_status}] s v
      puts "SUPPORT_BEFORE $h $s $v"
      if {$h eq $obligation || $s ne "proven" || $v ne "proven"} {
        error "Support $h is not a valid previously proven theorem"
      }
    }
    set selected [linsert $support 0 $obligation]
    puts "PROOF_SELECTED $selected"
    set_proven_directive true
    prove -property $selected -engine_mode {B H N} -time_limit 20s
    record_property $obligation
    lassign [get_property_info $obligation -list {status validity_status}] s v
    if {$s ne "proven" || $v ne "proven"} {error "Failed proof gate: $obligation"}
  }

  prove_with_support h_ab {}
  prove_with_support parcel_pipe.p_delivery {h_ab}
  report -file [file join $evidence_dir refined.txt] -detailed
} message]} {
  puts "FATAL $message"
  puts $::errorInfo
  exit 1
}
exit 0
