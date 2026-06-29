set bench_dir $::env(BENCH_DIR)
set run_dir $::env(RUN_DIR)

clear -all

analyze -sv09 "$bench_dir/simple_mem_design.sv" "$bench_dir/mem_ctrl_top.sv"
elaborate -top mem_ctrl_top

clock clk
reset rst

prove -all

report -summary

exit
