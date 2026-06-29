
module test (clk,rst,counter1,counter2);
  input clk,rst;
  output [31:0] counter1, counter2;
  reg    [31:0] counter1, counter2;
  always @(posedge clk or posedge rst) begin
     if (rst) begin
        counter1 = 0;
        counter2 = 0;
     end
     else begin
        counter1 = counter1 + 1;
        counter2 = counter2 + 1;
     end
  end
  assert property (@(posedge clk) &counter1 |-> &counter2);
endmodule
