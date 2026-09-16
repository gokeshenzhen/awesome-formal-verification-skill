// Allocation consumes credit now; retirement/refund credits arrive two cycles later.
module credit_return (
  input logic clk_i, rst_ni,
  input logic alloc_fire_i,
  input logic [7:0] alloc_units_i,
  input logic [8:0] refund_i,
  output logic [7:0] free_o,
  output logic [8:0] stage0_o, stage1_o
);
  always_ff @(posedge clk_i or negedge rst_ni) begin
    if (!rst_ni) begin
      free_o <= 8'hff;
      stage0_o <= '0;
      stage1_o <= '0;
    end else begin
      stage0_o <= refund_i;
      stage1_o <= stage0_o;
      free_o <= {1'b0, free_o} + stage1_o
                - (alloc_fire_i ? {1'b0, alloc_units_i} : 9'd0);
    end
  end
endmodule
