analyze -sv cnt_abstract_eg.sv no_skill/cnt_abstract_eg_checker.sv
elaborate

clock clk
reset -formal ~rst_n -bound 1

prove -all

report -summary
exit
