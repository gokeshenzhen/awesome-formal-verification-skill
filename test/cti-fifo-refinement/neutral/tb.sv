`default_nettype none
// Evaluator-authored observer. DUT is the unmodified non-FORMAL sfifo implementation.
module testbench(input wire clk, reset, wr, rd, input wire [31:0] data,
                 input wire [5:0] watched_address);
  wire full, empty;
  wire [5:0] fill;
  wire [31:0] out_data;
  sfifo #(.BW(32), .LGFLEN(5), .OPT_ASYNC_READ(0),
          .OPT_WRITE_ON_FULL(0), .OPT_READ_ON_EMPTY(0)) dut (
    .i_clk(clk), .i_reset(reset), .i_wr(wr), .i_data(data), .o_full(full),
    .o_fill(fill), .i_rd(rd), .o_data(out_data), .o_empty(empty));
  reg [31:0] watched_data;
  always @(posedge clk)
    if (!reset && wr && !full && dut.wr_addr == watched_address)
      watched_data <= data;
  A_symbol: assume property (@(posedge clk) 1'b1 |=> $stable(watched_address));
  P0: assert property (@(posedge clk) disable iff (reset)
    !empty && dut.rd_addr == watched_address |-> out_data == watched_data);
  C_read: cover property (@(posedge clk) disable iff (reset)
    !empty && rd && dut.rd_addr == watched_address);
endmodule
