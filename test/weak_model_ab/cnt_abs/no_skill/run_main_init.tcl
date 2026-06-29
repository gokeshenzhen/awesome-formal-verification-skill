analyze -sv cnt_abstract_eg.sv no_skill/cnt_abstract_eg_checker.sv
elaborate

clock clk
reset -init_state no_skill/init_reset.txt

prove -all
report -summary
exit
