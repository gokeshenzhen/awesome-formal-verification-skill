clear -all
analyze -sv09 /opt/preflight/smoke.sv
elaborate -top environment_smoke
clock clk
reset -expression {rst}
assert -name environment_assert {q == q}
cover -name environment_cover {q == 1'b1}
prove -all -time_limit 3s
puts "ENVIRONMENT_ASSERT_STATUS [get_property_info environment_assert -list status]"
puts "ENVIRONMENT_COVER_STATUS [get_property_info environment_cover -list status]"
report -summary
exit
