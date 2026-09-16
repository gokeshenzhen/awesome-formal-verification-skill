clear -all
set CASE_DIR /home/robin/Projects/awesome-formal-verification-skill/test/epoch_return_orig
analyze -sv09 [file join $CASE_DIR request_slots.sv] \
  [file join $CASE_DIR completion_queue.sv] [file join $CASE_DIR credit_return.sv] \
  [file join $CASE_DIR epoch_return_orig.sv]
elaborate -top epoch_return_orig
clock clk_i
reset -expression {!rst_ni}
set P0 epoch_return_orig.P0
set_prove_orchestration off
set_proofmaster off
prove -property $P0 -engine_mode {H AM N} \
  -per_property_time_limit_factor 0 -per_property_time_limit 15s -time_limit 15s
report -summary
puts "PROPERTY_INFO_BEGIN $P0"
puts "PROPERTY_INFO_FIELDS status validity_status run_status min_length max_length trace_length engine time trace_id"
puts [get_property_info $P0 -list {status validity_status run_status min_length max_length trace_length engine time trace_id}]
puts "PROPERTY_INFO_END $P0"
exit
