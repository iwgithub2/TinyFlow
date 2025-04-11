
module TESTER (
  input clk,
  output reg unsigned data
);

logic a[4:0];

assign a[4] = ~1'b1;

endmodule
