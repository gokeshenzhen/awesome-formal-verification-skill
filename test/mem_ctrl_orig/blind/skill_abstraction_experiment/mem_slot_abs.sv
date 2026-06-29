// mem_slot_abs.sv — Disclosed memory abstraction (NOT original RTL)
//
// Single-slot abstract model tracking only the word at the assertion's
// own symbolic NDC address (ndc_addr). Bound into the simple_mem wrapper
// via a `bind` statement at elaboration time.
//
// Signoff status: disclosed trusted-abstraction helper.
// This module is NOT part of the DUT. It replaces the 512x32 mem_imp
// array (16,384 flops) with one 32-bit tracked register, which is sound
// for the mem_works_ndc property because:
//   - The property only reads/writes at addr==ndc_addr.
//   - Reads at other addresses are left free (unconstrained), which is
//     safe because mem_works_ndc's consequent only fires on addr==ndc_addr.

module mem_slot_abs #(
  parameter ADDR_WIDTH = 9,
  parameter DATA_WIDTH = 32
)(
  input  logic                  clk,
  input  logic                  rst,
  input  logic [ADDR_WIDTH-1:0] addr,
  input  logic [DATA_WIDTH-1:0] din,
  input  logic                  op,          // 0=OP_RD, 1=OP_WR
  input  logic [ADDR_WIDTH-1:0] ndc_addr,   // the stable symbolic address
  // Outputs — reconnect to boxed m1.dout so the assertion can observe them
  output logic [DATA_WIDTH-1:0] tracked,     // last value written at ndc_addr
  output logic                  rd_ndc_q,    // registered: previous cycle was a read at ndc_addr
  output logic [DATA_WIDTH-1:0] tracked_q    // registered tracked (aligned with rd_ndc_q)
);

  // Track only the word at ndc_addr
  always_ff @(posedge clk or posedge rst) begin
    if (rst) begin
      tracked   <= '0;
      rd_ndc_q  <= 1'b0;
      tracked_q <= '0;
    end else begin
      // Write: update slot only when the current address matches ndc_addr
      if (op == 1'b1 && addr == ndc_addr)   // OP_WR=1
        tracked <= din;

      // Registered read-at-ndc indicator (one cycle delayed, for $past-free contract)
      rd_ndc_q  <= (op == 1'b0) && (addr == ndc_addr);  // OP_RD=0
      tracked_q <= tracked;
    end
  end

endmodule
