// Four independent MAC4_LANE units sharing clock, reset and control.
//   lane k multiplies a[4k+3:4k] * b[4k+3:4k] and accumulates into acc[12k+11:12k].
// Four lanes (about 90 flip-flops) give the clock tree something to balance.
module MAC4 (
    input             clk,
    input             rst_n,
    input             clr,
    input             en,
    input      [15:0] a,
    input      [15:0] b,
    output     [47:0] acc
);
    genvar k;
    generate
        for (k = 0; k < 4; k = k + 1) begin : lane
            MAC4_LANE u (.clk(clk), .rst_n(rst_n), .clr(clr), .en(en),
                         .a(a[4*k +: 4]), .b(b[4*k +: 4]), .acc(acc[12*k +: 12]));
        end
    endgenerate
endmodule
