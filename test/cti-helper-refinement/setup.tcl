set example_dir [file dirname [file normalize [info script]]]
set evidence_dir [file join $example_dir evidence]
file mkdir $evidence_dir
clear -all
analyze -sv [file join $example_dir parcel_pipe.sv]
elaborate -top parcel_pipe
clock clk
reset -expression {!rst_n}
set_proofmaster off
set_prove_orchestration off

proc record_property {p} {
  puts "PROPERTY_FIELDS name status validity_status min_length max_length engine time trace_id"
  puts "PROPERTY_RESULT $p [get_property_info $p -list {status validity_status min_length max_length engine time trace_id}]"
}

proc save_sst {p stem} {
  global evidence_dir
  record_property $p
  set tid [get_property_info $p -list trace_id]
  if {$tid eq ""} {error "No SST diagnostic attached to $p"}
  set metadata [get_trace_info $tid]
  puts "TRACE_METADATA $p $metadata"
  array set m $metadata
  if {![info exists m(tag)] || $m(tag) ne "SST"} {error "Expected SST tag"}
  visualize -violation -sst -property $p -trace_id $tid -new_window $stem
  visualize -save -vcd [file join $evidence_dir ${stem}.vcd] -force -window $stem
}
