if {[catch {
  source [file join [file dirname [info script]] setup.tcl]
  puts "TEACHING_BASELINE: ordinary reset-based proof, no helper"
  prove -property parcel_pipe.p_delivery -engine_mode {B H N} -time_limit 20s
  record_property parcel_pipe.p_delivery
  cover -name c_delivery {valid[2] && data_c == 2'd3}
  cover -name c_bubble_stale {!valid[0] && data_a != ref_a}
  prove -property {c_delivery c_bubble_stale} -engine_mode B -time_limit 20s
  record_property c_delivery
  record_property c_bubble_stale
  report -file [file join $evidence_dir baseline.txt] -detailed
} message]} {
  puts "FATAL $message"
  puts $::errorInfo
  exit 1
}
exit 0
