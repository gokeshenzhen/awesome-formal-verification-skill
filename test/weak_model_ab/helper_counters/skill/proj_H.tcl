clear -all
analyze -sv two_counters.v
elaborate -top test
clock clk
reset rst
sanity_check
check_assumptions
assert -helper -name eq_cnt { @(posedge clk) counter1 == counter2 }
set_prove_orchestration off
set_engine_mode H
set_prove_per_property_time_limit 10m
prove -property {eq_cnt}
prove -with_helpers -property {<embedded>::test._assert_1}
puts "STATUS_EQ=[get_property_info -list status eq_cnt]"
puts "STATUS_ASSERT=[get_property_info -list status <embedded>::test._assert_1]"
puts "STATUS_PRE=[get_property_info -list status <embedded>::test._assert_1:precondition1]"
report -summary -result -force -file skill/proj_H_summary.rpt
