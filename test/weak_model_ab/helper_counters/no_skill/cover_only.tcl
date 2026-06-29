analyze -sv two_counters.v
elaborate -top test
clock clk
reset rst
set_max_trace_length 40
cover -name antecedent_reachable { @(posedge clk) &counter1 }
prove -all
report -all
exit
