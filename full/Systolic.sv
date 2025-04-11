module SystolicArray #(
    parameter size = 3,
    parameter n = 16,
    parameter d = 8
) (
    input  logic clk,
    input  logic reset,
    input  logic r_en            [size],
    input  logic c_en            [size],
    input  logic [n-1:0] t_w_in  [size],
    input  logic [n-1:0] l_x_in  [size],
    input  logic [$clog2(size)-1:0] s_row,
    input  logic [$clog2(size)-1:0] s_col,
    output logic [n-1:0] b_s_out
);

logic [n-1:0] w[size+1][size];
logic [n-1:0] x[size][size+1];
logic [n-1:0] s[size][size];

assign b_s_out = s[s_row][s_col];

genvar i, j;
generate for (j = 0; j < size; j++) begin : g_first_row
    assign w[0][j] = t_w_in[j];
end endgenerate

generate for (i = 0; i < size; i++) begin : g_first_col
    assign x[i][0] = l_x_in[i];
end endgenerate

generate for (i = 0; i < size; i++) begin : g_row
    for (j = 0; j < size; j++) begin : g_cols
       SystolicMMPE #(
        .n(n),
        .d(d),
        .sign(1)
       ) (
        .clk(clk),
        .reset(reset),
        .en(r_en[i] && c_en[j]),
        .x_in(x[i][j]),
        .w_in(w[i][j]),
        .x_out(x[i][j+1]),
        .w_out(w[i+1][j]),
        .s_out(s[i][j])
       );
    end
end endgenerate

endmodule