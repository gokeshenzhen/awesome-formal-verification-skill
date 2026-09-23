if {[catch {
  source [file join [file dirname [info script]] setup.tcl]
  puts "TEACHING_DIAGNOSTIC: fresh arbitrary-state SST; not an ordinary proof timeout"
  puts "SST_RETURN [prove -property parcel_pipe.p_delivery -sst 2 -prefer_quiet -engine_mode B -time_limit 10s]"
  save_sst parcel_pipe.p_delivery target_sst
  report -file [file join $evidence_dir target_sst.txt] -detailed
} message]} {
  puts "FATAL $message"
  puts $::errorInfo
  exit 1
}
exit 0
