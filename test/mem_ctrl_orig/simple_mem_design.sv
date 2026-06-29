typedef enum logic {OP_RD, OP_WR} t_op;

parameter ADDR_WIDTH = 9;
parameter ADDR_NUM = 512;
parameter DATA_WIDTH = 32;

module mem_imp (
  input  logic                  clk,
  input  logic                  rst,
  input  logic [ADDR_WIDTH-1:0] addr,
  input  logic [DATA_WIDTH-1:0] din,
  input  t_op                   op,
  output logic [DATA_WIDTH-1:0] dout
);

  logic [DATA_WIDTH-1:0] mem_content [ADDR_NUM-1:0];

  always_ff @(posedge clk or posedge rst) begin
    if (rst) begin
      mem_content <= '{default: '0};
      dout <= '0;
    end else begin
      if (op == OP_RD) begin
        dout <= mem_content[addr];
      end else if (op == OP_WR) begin
        dout <= '0;
        mem_content[addr] <= din;
      end
    end
  end

endmodule

module simple_mem (
  input  logic                  clk,
  input  logic                  rst,
  input  logic [ADDR_WIDTH-1:0] addr,
  input  logic [DATA_WIDTH-1:0] din,
  input  t_op                   op,
  output logic [DATA_WIDTH-1:0] dout_final
);

  logic [DATA_WIDTH-1:0] dout;

  default clocking cb @(posedge clk);
  endclocking
  default disable iff (rst);

  mem_imp m1 (
    .clk(clk),
    .rst(rst),
    .addr(addr),
    .din(din),
    .op(op),
    .dout(dout)
  );

  logic [ADDR_WIDTH-1:0] ndc_addr;
  logic [DATA_WIDTH-1:0] ndc_data;

  stable_addr: assume property (##1 $stable(ndc_addr));
  stable_data: assume property (##1 $stable(ndc_data));

  logic addr_read;
  logic addr_write;
  logic symbol_write;

  assign addr_read = (op == OP_RD) && (addr == ndc_addr);
  assign addr_write = (op == OP_WR) && (addr == ndc_addr);
  assign symbol_write = addr_write && (din == ndc_data);

  mem_works_ndc: assert property (
    symbol_write ##1 (!addr_write)[*1:$] ##1 addr_read |=> (dout_final == ndc_data)
  );

  assign dout_final = dout;

endmodule
