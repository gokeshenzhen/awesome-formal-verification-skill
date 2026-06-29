analyze -sv cnt_abstract_eg.sv no_skill/reach_checker.sv no_skill/bind_reach_b.sv
elaborate

clock clk
reset -init_state no_skill/init_b.txt

prove -all
report -summary
exit
