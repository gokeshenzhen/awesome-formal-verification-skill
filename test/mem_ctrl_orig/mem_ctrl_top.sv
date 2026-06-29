module mem_ctrl_top (
  input  logic                  clk,
  input  logic                  rst,
  input  logic                  start,
  input  logic [ADDR_WIDTH-1:0] req_addr,
  input  logic [DATA_WIDTH-1:0] req_wdata,
  output logic                  done,
  output logic [DATA_WIDTH-1:0] read_data
);

  typedef enum logic [2:0] {
    S_IDLE,
    S_WRITE,
    S_READ,
    S_CHECK,
    S_DONE
  } state_t;

  state_t state;
  logic [ADDR_WIDTH-1:0] saved_addr;
  logic [DATA_WIDTH-1:0] saved_data;

  logic [ADDR_WIDTH-1:0] mem_addr;
  logic [DATA_WIDTH-1:0] mem_din;
  t_op mem_op;

  simple_mem u_mem (
    .clk(clk),
    .rst(rst),
    .addr(mem_addr),
    .din(mem_din),
    .op(mem_op),
    .dout_final(read_data)
  );

  always_comb begin
    mem_addr = saved_addr;
    mem_din = saved_data;
    mem_op = OP_RD;
    done = 1'b0;

    unique case (state)
      S_IDLE: begin
        mem_addr = req_addr;
        mem_din = req_wdata;
      end
      S_WRITE: begin
        mem_addr = saved_addr;
        mem_din = saved_data;
        mem_op = OP_WR;
      end
      S_READ: begin
        mem_addr = saved_addr;
        mem_op = OP_RD;
      end
      S_CHECK: begin
        mem_addr = saved_addr;
        mem_op = OP_RD;
      end
      S_DONE: begin
        mem_addr = saved_addr;
        mem_op = OP_RD;
        done = 1'b1;
      end
      default: begin
        mem_addr = saved_addr;
        mem_op = OP_RD;
      end
    endcase
  end

  always_ff @(posedge clk or posedge rst) begin
    if (rst) begin
      state <= S_IDLE;
      saved_addr <= '0;
      saved_data <= '0;
    end else begin
      unique case (state)
        S_IDLE: begin
          if (start) begin
            saved_addr <= req_addr;
            saved_data <= req_wdata;
            state <= S_WRITE;
          end
        end
        S_WRITE: state <= S_READ;
        S_READ:  state <= S_CHECK;
        S_CHECK: state <= S_DONE;
        S_DONE:  state <= S_IDLE;
        default: state <= S_IDLE;
      endcase
    end
  end

  default clocking cb @(posedge clk);
  endclocking
  default disable iff (rst);

  ctrl_readback_ok: assert property (
    state == S_CHECK |-> read_data == saved_data
  );

  ctrl_transaction_seen: cover property (
    state == S_IDLE ##1 state == S_WRITE ##1 state == S_READ ##1 state == S_CHECK
  );

endmodule
