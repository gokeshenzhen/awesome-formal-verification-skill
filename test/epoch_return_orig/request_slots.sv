// Client-visible requests. A flushed/cancelled request may still be in flight.
module request_slots (
  input logic clk_i, rst_ni, flush_i,
  input logic alloc_fire_i, alloc_slot_i,
  input logic [7:0] alloc_units_i,
  input logic issue_fire_i, issue_slot_i,
  input logic cancel_fire_i, cancel_slot_i,
  input logic retire_fire_i, retire_slot_i,
  output logic [1:0] live_o, issued_o, epoch_o,
  output logic [1:0][7:0] units_o
);
  always_ff @(posedge clk_i or negedge rst_ni) begin
    if (!rst_ni) begin
      live_o <= '0;
      issued_o <= '0;
      epoch_o <= '0;
      units_o <= '0;
    end else if (flush_i) begin
      live_o <= '0;
      issued_o <= '0;
    end else begin
      if (cancel_fire_i) begin
        live_o[cancel_slot_i] <= 1'b0;
        issued_o[cancel_slot_i] <= 1'b0;
      end
      if (retire_fire_i) begin
        live_o[retire_slot_i] <= 1'b0;
        issued_o[retire_slot_i] <= 1'b0;
      end
      if (issue_fire_i) issued_o[issue_slot_i] <= 1'b1;
      if (alloc_fire_i) begin
        live_o[alloc_slot_i] <= 1'b1;
        issued_o[alloc_slot_i] <= 1'b0;
        epoch_o[alloc_slot_i] <= !epoch_o[alloc_slot_i];
        units_o[alloc_slot_i] <= alloc_units_i;
      end
    end
  end
endmodule
