analyze -sv two_counters.v
elaborate -top test
clock clk
reset rst
cover -name antecedent_reachable { @(posedge clk) &counter1 }
prove -all
cover -all
report -all
exit
