module cnt_abstract_eg_checker (
  input logic        clk,
  input logic        rst_n,
  input logic [31:0] cntr,
  input logic        A,
  input logic        B,
  input logic        C,
  input logic        D
);
  localparam logic [31:0] A_TGT = 32'd8369262;
  localparam logic [31:0] B_TGT = 32'd268407145;

  default clocking cb @(posedge clk); endclocking
  default disable iff (!rst_n);

  // Output intent from the RTL:
  // - A and B are sticky set-once flags.
  // - C and D are never driven high.
  A_set: assert property (cntr == A_TGT |=> A);
  B_set: assert property (cntr == B_TGT |=> B);
  A_sticky: assert property (A |=> A);
  B_sticky: assert property (B |=> B);
  C_low: assert property (C == 1'b0);
  D_low: assert property (D == 1'b0);

  // Non-vacuity witnesses for the counter milestones that trigger A/B.
  reach_A: cover property (cntr == A_TGT);
  reach_B: cover property (cntr == B_TGT);
endmodule

bind cnt_abstract_eg cnt_abstract_eg_checker u_cnt_abstract_eg_checker (
  .clk(clk),
  .rst_n(rst_n),
  .cntr(cntr),
  .A(A),
  .B(B),
  .C(C),
  .D(D)
);
