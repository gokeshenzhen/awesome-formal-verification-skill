module epoch_return_orig (
  input logic clk_i, rst_ni,
  input logic alloc_i, alloc_slot_i,
  input logic [7:0] alloc_units_i,
  input logic issue_i, issue_slot_i, issue_entry_i,
  input logic complete_i, complete_entry_i, take_i,
  input logic cancel_i, cancel_slot_i, flush_i,
  output logic [7:0] free_o,
  output logic idle_o
);
  logic [1:0] live, issued, epoch;
  logic [1:0][7:0] units;
  logic [1:0] queue_valid, queue_slot, queue_epoch;
  logic [1:0][7:0] queue_units;
  logic response_valid, response_slot, response_epoch;
  logic [7:0] response_units;
  logic [8:0] refund, return0, return1;
  logic alloc_fire, issue_fire, cancel_fire, retire_fire, reuse_blocked;

  // A one-bit generation tag cannot be reused while an old copy is in flight.
  always_comb begin
    reuse_blocked = response_valid && response_slot == alloc_slot_i &&
                    response_epoch == !epoch[alloc_slot_i];
    for (int k = 0; k < 2; k++) begin
      reuse_blocked |= queue_valid[k] && queue_slot[k] == alloc_slot_i &&
                       queue_epoch[k] == !epoch[alloc_slot_i];
    end
  end

  assign alloc_fire = alloc_i && !flush_i && !live[alloc_slot_i] &&
                      !reuse_blocked && alloc_units_i != 0 && alloc_units_i <= free_o;
  assign cancel_fire = cancel_i && !flush_i && live[cancel_slot_i];
  assign retire_fire = response_valid && take_i && !flush_i &&
                       live[response_slot] && epoch[response_slot] == response_epoch &&
                       !(cancel_fire && cancel_slot_i == response_slot);
  assign issue_fire = issue_i && !flush_i && live[issue_slot_i] &&
                      !issued[issue_slot_i] && !queue_valid[issue_entry_i] &&
                      !(cancel_fire && cancel_slot_i == issue_slot_i) &&
                      !(retire_fire && response_slot == issue_slot_i);

  // Cancellation/flush uses the client table. Completion uses the queued payload.
  always_comb begin
    refund = '0;
    if (flush_i) begin
      for (int k = 0; k < 2; k++)
        refund += live[k] ? {1'b0, units[k]} : 9'd0;
    end else begin
      if (cancel_fire) refund += {1'b0, units[cancel_slot_i]};
      if (retire_fire) refund += {1'b0, response_units};
    end
  end

  request_slots u_slots (
    .clk_i, .rst_ni, .flush_i, .alloc_fire_i(alloc_fire), .alloc_slot_i, .alloc_units_i,
    .issue_fire_i(issue_fire), .issue_slot_i, .cancel_fire_i(cancel_fire), .cancel_slot_i,
    .retire_fire_i(retire_fire), .retire_slot_i(response_slot),
    .live_o(live), .issued_o(issued), .epoch_o(epoch), .units_o(units)
  );
  completion_queue u_queue (
    .clk_i, .rst_ni, .issue_fire_i(issue_fire), .issue_entry_i, .issue_slot_i,
    .issue_epoch_i(epoch[issue_slot_i]), .issue_units_i(units[issue_slot_i]),
    .complete_i, .complete_entry_i, .take_i,
    .valid_o(queue_valid), .slot_o(queue_slot), .epoch_o(queue_epoch), .units_o(queue_units),
    .response_valid_o(response_valid), .response_slot_o(response_slot),
    .response_epoch_o(response_epoch), .response_units_o(response_units)
  );
  credit_return u_credit (
    .clk_i, .rst_ni, .alloc_fire_i(alloc_fire), .alloc_units_i, .refund_i(refund),
    .free_o, .stage0_o(return0), .stage1_o(return1)
  );

  // Idle describes client-visible work and its refunds, not transport drain.
  assign idle_o = !(|live) && return0 == 0 && return1 == 0;
  P0: assert property (@(posedge clk_i) disable iff (!rst_ni)
                       idle_o |-> free_o == 8'hff);
endmodule
