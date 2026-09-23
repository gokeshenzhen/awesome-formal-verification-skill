proc add_helpers {refined} {
    assert -name H_fill_ptr {dut.o_fill == dut.wr_addr - dut.rd_addr}
    assert -name H_empty_fill {dut.o_empty == (dut.o_fill == 0)}
    assert -name H_full_fill {dut.o_full == (dut.o_fill == 6'd32)}
    assert -name H_mem_watch_live {((watched_address - dut.rd_addr) < dut.o_fill) |-> dut.mem[watched_address[4:0]] == watched_data}
    assert -name H_rd_data_mem {(!dut.o_empty && !dut.REGISTERED_READ.bypass_valid) |-> dut.REGISTERED_READ.rd_data == dut.mem[dut.rd_addr[4:0]]}
    assert -name H_bypass_head_data {(!dut.o_empty && dut.rd_addr == watched_address && dut.REGISTERED_READ.bypass_valid) |-> dut.REGISTERED_READ.bypass_data == watched_data}
    assert -name H_rd_head_data {(!dut.o_empty && dut.rd_addr == watched_address && !dut.REGISTERED_READ.bypass_valid) |-> dut.REGISTERED_READ.rd_data == watched_data}
    if {$refined} {
        # The SST exposes a missing reachable-state invariant.
        assert -name H_fill_range {dut.o_fill <= 6'd32}
    }
}

proc prove_control_helpers {refined} {
    prove_checked H_fill_ptr {} 8s
    set support {H_fill_ptr}
    if {$refined} {
        prove_checked H_fill_range $support 12s
        lappend support H_fill_range
    }
    prove_checked H_empty_fill $support 8s
    prove_checked H_full_fill $support 8s
    return [concat $support {H_empty_fill H_full_fill}]
}
