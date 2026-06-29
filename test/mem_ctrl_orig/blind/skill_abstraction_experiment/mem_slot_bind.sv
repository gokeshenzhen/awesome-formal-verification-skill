// mem_slot_bind.sv — Disclosed abstraction helper for simple_mem
//
// Binds a single-slot abstract memory tracker into the simple_mem module.
// This is NOT part of the DUT; it is a disclosed trusted-abstraction helper.
//
// Tracking logic:
//   - tracked: the last value written to ndc_addr
//   - rd_ndc_q: registered "previous-cycle read at ndc_addr" flag
//   - tracked_q: registered tracked value (aligned for $past-free contract)
//
// The memory contract assume in the TCL script uses rd_ndc_q and tracked_q
// to reconnect the black-boxed m1.dout output without using $past().

module mem_slot_abs #(
  parameter ADDR_WIDTH = 9,
  parameter DATA_WIDTH = 32
)(
  input  logic                  clk,
  input  logic                  rst,
  input  logic [ADDR_WIDTH-1:0] addr,
  input  logic [DATA_WIDTH-1:0] din,
  input  logic                  op,          // 0=OP_RD (t_op::OP_RD=0), 1=OP_WR
  input  logic [ADDR_WIDTH-1:0] ndc_addr
);

  logic [DATA_WIDTH-1:0] tracked;     // last value written to ndc_addr
  logic                  rd_ndc_q;   // registered: prev cycle read at ndc_addr
  logic [DATA_WIDTH-1:0] tracked_q;  // registered tracked (for $past-free contract)

  always_ff @(posedge clk or posedge rst) begin
    if (rst) begin
      tracked   <= '0;
      rd_ndc_q  <= 1'b0;
      tracked_q <= '0;
    end else begin
      if (op == 1'b1 && addr == ndc_addr)
        tracked <= din;
      rd_ndc_q  <= (op == 1'b0) && (addr == ndc_addr);
      tracked_q <= tracked;
    end
  end

endmodule

// Bind the tracker into every instance of simple_mem
bind simple_mem mem_slot_abs #(
  .ADDR_WIDTH(ADDR_WIDTH),
  .DATA_WIDTH(DATA_WIDTH)
) u_abs (
  .clk      (clk),
  .rst      (rst),
  .addr     (addr),
  .din      (din),
  .op       (op),
  .ndc_addr (ndc_addr)
);
