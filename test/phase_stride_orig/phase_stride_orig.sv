module phase_stride_orig (
  input  logic        clk,
  input  logic        rst_n,
  input  logic        stride_sel,
  input  logic        challenge_bit,
  input  logic [3:0]  route_00,
  input  logic [3:0]  route_01,
  input  logic [3:0]  route_02,
  input  logic [3:0]  route_03,
  input  logic [3:0]  route_04,
  input  logic [3:0]  route_05,
  input  logic [3:0]  route_06,
  input  logic [3:0]  route_07,
  input  logic [3:0]  route_08,
  input  logic [3:0]  route_09,
  input  logic [3:0]  route_10,
  input  logic [3:0]  route_11,
  input  logic [3:0]  route_12,
  input  logic [3:0]  route_13,
  input  logic [3:0]  route_14,
  input  logic [3:0]  route_15,
  input  logic [3:0]  route_16
);

  logic [8:0] phase_code;
  logic [6:0] warmup_count;
  logic [31:0] challenge_history;
  logic [3:0] route [0:16];
  logic       all_routes_distinct;
  logic       bad_event;

  function automatic logic [8:0] phase_step(input logic [8:0] value);
    phase_step = {value[7:0], value[8] ^ value[4]};
  endfunction

  function automatic logic [8:0] phase_step_17(input logic [8:0] value);
    logic [8:0] next_value;
    integer k;
    begin
      next_value = value;
      for (k = 0; k < 17; k = k + 1)
        next_value = phase_step(next_value);
      phase_step_17 = next_value;
    end
  endfunction

  assign route[0]  = route_00;
  assign route[1]  = route_01;
  assign route[2]  = route_02;
  assign route[3]  = route_03;
  assign route[4]  = route_04;
  assign route[5]  = route_05;
  assign route[6]  = route_06;
  assign route[7]  = route_07;
  assign route[8]  = route_08;
  assign route[9]  = route_09;
  assign route[10] = route_10;
  assign route[11] = route_11;
  assign route[12] = route_12;
  assign route[13] = route_13;
  assign route[14] = route_14;
  assign route[15] = route_15;
  assign route[16] = route_16;

  integer i;
  integer j;
  always_comb begin
    all_routes_distinct = 1'b1;
    for (i = 0; i < 17; i = i + 1)
      for (j = i + 1; j < 17; j = j + 1)
        if (route[i] == route[j])
          all_routes_distinct = 1'b0;
  end

  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      phase_code <= 9'h001;
      warmup_count <= '0;
      challenge_history <= '0;
    end else if (warmup_count != 7'd96) begin
      warmup_count <= warmup_count + 1'b1;
      phase_code <= phase_code;
      challenge_history <= {challenge_history[30:0], challenge_bit};
    end else begin
      phase_code <= stride_sel
                  ? phase_step_17(phase_code)
                  : phase_step(phase_code);
      warmup_count <= warmup_count;
      challenge_history <= {challenge_history[30:0], challenge_bit};
    end
  end

  assign bad_event =
      all_routes_distinct ||
      ((phase_code == 9'h0c7) &&
       (challenge_history == 32'h6d3a_91c5));

  default clocking cb @(posedge clk); endclocking
  default disable iff (!rst_n);

  P0: assert property (!bad_event);

endmodule
