clear -all

if {[info exists ::env(CASE_DIR)]} {
  set CASE_DIR [file normalize $::env(CASE_DIR)]
} else {
  set CASE_DIR [file normalize \
    /home/robin/Projects/awesome-formal-verification-skill/test/phase_stride_orig]
}

analyze -sv09 [file join $CASE_DIR phase_stride_orig.sv]
elaborate -top phase_stride_orig
clock clk
reset -expression {!rst_n}

set P0 phase_stride_orig.P0

set_prove_orchestration off
prove -property $P0 \
  -engine_mode N \
  -per_property_time_limit_factor 0 \
  -per_property_time_limit 15s \
  -time_limit 15s

report -summary
puts "PROPERTY_INFO_BEGIN $P0"
puts [get_property_info $P0 \
  -list {status min_length max_length trace_length engine time trace_id}]
puts "PROPERTY_INFO_END $P0"

exit
