clear -all
analyze -sv cnt_abstract_eg.sv skill/cnt_abstract_eg_checker.sv
elaborate -top cnt_abstract_eg
clock clk
reset ~rst_n

# Milestone abstraction keeps the deep counter proof tractable and gives
# shallow witnesses for the exact trigger values.
abstract -counter cntr -values 0 8369262 268407145

sanity_check
check_assumptions
prove -all
report -summary -result -force -file skill/final_report.rpt
