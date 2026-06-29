module cnt_reach_checker #(
    parameter logic [31:0] THR = 32'd0
) (
    input logic        clk,
    input logic        sig,
    input logic [31:0] cntr
);

  cover property (@(posedge clk) sig);

endmodule
