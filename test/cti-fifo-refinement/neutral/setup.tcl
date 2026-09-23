set case_dir [file dirname [file normalize [info script]]]
clear -all
analyze -sv12 [file join $case_dir sfifo.v] [file join $case_dir tb.sv]
elaborate -top testbench
clock clk
reset -expression {reset}
set_prove_orchestration off
set_proofmaster off
