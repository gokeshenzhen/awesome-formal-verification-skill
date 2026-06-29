module cnt_abstract_eg_checker (
    input logic        clk,
    input logic        rst_n,
    input logic        A,
    input logic        B,
    input logic        C,
    input logic        D,
    input logic [31:0] cntr
);

  localparam logic [31:0] THR_A = 32'd8369262;
  localparam logic [31:0] THR_B = 32'd268407145;

  // C and D are only driven in reset and must remain low.
  assert property (@(posedge clk) disable iff (!rst_n) !C);
  assert property (@(posedge clk) disable iff (!rst_n) !D);

  // A and B become high once their counter thresholds are reached, then stay high.
  assert property (@(posedge clk) disable iff (!rst_n) (cntr == THR_A) |=> A);
  assert property (@(posedge clk) disable iff (!rst_n) A |=> A);

  assert property (@(posedge clk) disable iff (!rst_n) (cntr == THR_B) |=> B);
  assert property (@(posedge clk) disable iff (!rst_n) B |=> B);

endmodule

bind cnt_abstract_eg cnt_abstract_eg_checker u_cnt_abstract_eg_checker (
  .clk(clk),
  .rst_n(rst_n),
  .A(A),
  .B(B),
  .C(C),
  .D(D),
  .cntr(cntr)
);
