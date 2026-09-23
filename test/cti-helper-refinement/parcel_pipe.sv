// Three parcel desks: A (receive) -> B (buffer) -> C (dispatch).
// ref_* is a verification-only receipt pipeline, not extra DUT hardware.
module parcel_pipe (
  input  logic       clk, rst_n, step, in_valid,
  input  logic [1:0] in_data,
  output logic       out_valid,
  output logic [1:0] out_data
);
  logic [2:0] valid;
  logic [1:0] data_a, data_b, data_c;
  logic [1:0] ref_a, ref_b, ref_c;

  assign out_valid = valid[2];
  assign out_data  = data_c;

  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      valid <= '0;
      data_a <= '0; data_b <= '0; data_c <= '0;
    end else if (step) begin
      valid <= {valid[1:0], in_valid};
      if (in_valid) data_a <= in_data;
      if (valid[0]) data_b <= data_a;
      if (valid[1]) data_c <= data_b;
    end
  end

  // A deliberately simple independent data reference: shift even on bubbles.
  // Unoccupied desks may therefore contain stale data unlike their receipts.
  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      ref_a <= '0; ref_b <= '0; ref_c <= '0;
    end else if (step) begin
      ref_a <= in_data;
      ref_b <= ref_a;
      ref_c <= ref_b;
    end
  end

  p_delivery: assert property (@(posedge clk) disable iff (!rst_n)
    out_valid |-> out_data == ref_c);
endmodule
