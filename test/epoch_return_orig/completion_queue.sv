// Two independent in-flight entries; completion selection may be out of order.
module completion_queue (
  input logic clk_i, rst_ni,
  input logic issue_fire_i, issue_entry_i, issue_slot_i, issue_epoch_i,
  input logic [7:0] issue_units_i,
  input logic complete_i, complete_entry_i, take_i,
  output logic [1:0] valid_o, slot_o, epoch_o,
  output logic [1:0][7:0] units_o,
  output logic response_valid_o, response_slot_o, response_epoch_o,
  output logic [7:0] response_units_o
);
  logic complete_fire;
  assign complete_fire = complete_i && valid_o[complete_entry_i] && !response_valid_o;

  always_ff @(posedge clk_i or negedge rst_ni) begin
    if (!rst_ni) begin
      valid_o <= '0;
      slot_o <= '0;
      epoch_o <= '0;
      units_o <= '0;
      response_valid_o <= 1'b0;
      response_slot_o <= 1'b0;
      response_epoch_o <= 1'b0;
      response_units_o <= '0;
    end else begin
      if (take_i) response_valid_o <= 1'b0;
      if (complete_fire) begin
        valid_o[complete_entry_i] <= 1'b0;
        response_valid_o <= 1'b1;
        response_slot_o <= slot_o[complete_entry_i];
        response_epoch_o <= epoch_o[complete_entry_i];
        response_units_o <= units_o[complete_entry_i];
      end
      if (issue_fire_i) begin
        valid_o[issue_entry_i] <= 1'b1;
        slot_o[issue_entry_i] <= issue_slot_i;
        epoch_o[issue_entry_i] <= issue_epoch_i;
        units_o[issue_entry_i] <= issue_units_i;
      end
    end
  end
endmodule
