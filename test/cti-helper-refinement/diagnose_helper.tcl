if {[catch {
  source [file join [file dirname [info script]] setup.tcl]
  # target_sst shows a valid B parcel inconsistent with its receipt.
  assert -helper -name h_b {(!valid[1]) || (data_b == ref_b)}
  puts {HELPER_OLD (!valid[1]) || (data_b == ref_b)}
  puts "SST_RETURN [prove -property h_b -sst 2 -prefer_quiet -engine_mode B -time_limit 10s]"
  save_sst h_b helper_sst
  report -file [file join $evidence_dir helper_sst.txt] -detailed
} message]} {
  puts "FATAL $message"
  puts $::errorInfo
  exit 1
}
exit 0
