set bench_dir $::env(BENCH_DIR)

clear -all

analyze -sv09 "$bench_dir/simple_mem_design.sv" "$bench_dir/mem_ctrl_top.sv"
elaborate -top mem_ctrl_top

clock clk
reset rst

prove -property {mem_ctrl_top.ctrl_readback_ok}
prove -property {mem_ctrl_top.ctrl_transaction_seen}

report -summary

exit
