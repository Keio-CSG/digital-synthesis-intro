// 4x4 unsigned multiply-accumulate with registered inputs.
//   stage 1: a_q,b_q <= a,b           (input registers)
//   stage 2: acc     <= acc + a_q*b_q (accumulate, when en_q=1)
// clr (synchronous) restarts the accumulation.
module MAC4_LANE (
    input            clk,
    input            rst_n,   // asynchronous, active low
    input            clr,
    input            en,
    input      [3:0] a,
    input      [3:0] b,
    output reg [11:0] acc
);
    reg [3:0] a_q, b_q;
    reg       en_q, clr_q;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            a_q <= 4'd0; b_q <= 4'd0; en_q <= 1'b0; clr_q <= 1'b0;
        end else begin
            a_q <= a; b_q <= b; en_q <= en; clr_q <= clr;
        end
    end

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n)      acc <= 12'd0;
        else if (clr_q)  acc <= 12'd0;
        else if (en_q)   acc <= acc + a_q * b_q;
    end
endmodule
