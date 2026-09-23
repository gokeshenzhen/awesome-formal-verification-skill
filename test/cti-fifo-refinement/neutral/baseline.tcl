if {[catch {
  source setup.tcl
  file mkdir evidence
  prove -property testbench.P0 -engine_mode {H AM N} \
    -per_property_time_limit_factor 0 -per_property_time_limit 120s -time_limit 120s
  puts "BASELINE_FIELDS status validity_status min_length max_length engine time trace_id"
  puts "BASELINE_RESULT [get_property_info testbench.P0 -list {status validity_status min_length max_length engine time trace_id}]"
  report -file evidence/baseline.txt -detailed
} message]} {
  puts "BASELINE_ERROR $message"
  puts $::errorInfo
  exit 1
}
exit 0
