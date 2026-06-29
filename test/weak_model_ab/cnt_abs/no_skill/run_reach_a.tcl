analyze -sv cnt_abstract_eg.sv no_skill/reach_checker.sv no_skill/bind_reach_a.sv
elaborate

clock clk
reset -init_state no_skill/init_a.txt

prove -all
report -summary
exit
