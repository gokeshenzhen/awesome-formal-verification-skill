analyze -sv two_counters.v
elaborate -top test
clock clk
reset rst
prove -all
report -all
exit
