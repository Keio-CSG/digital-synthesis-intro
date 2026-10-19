`timescale 1ns/1ps
// Self-checking testbench: random vectors vs. a behavioural model.
module tb_MAC4;
    reg clk = 0, rst_n = 0, clr = 0, en = 0;
    reg [15:0] a = 0, b = 0;
    wire [47:0] acc;
    MAC4 dut (.clk(clk), .rst_n(rst_n), .clr(clr), .en(en), .a(a), .b(b), .acc(acc));

    real half = 5.0;                 // half period [ns], override with +HALF=<ns>
    integer ok_h;
    initial ok_h = $value$plusargs("HALF=%f", half);
    always #(half) clk = ~clk;

    // reference model of the 4 lanes, same 2-cycle latency
    reg [15:0] ma, mb; reg men, mclr; reg [47:0] macc;
    integer k;
    always @(posedge clk) begin
        for (k = 0; k < 4; k = k + 1)
            if (mclr)     macc[12*k +: 12] <= 0;
            else if (men) macc[12*k +: 12] <= macc[12*k +: 12] + ma[4*k +: 4] * mb[4*k +: 4];
        ma <= a; mb <= b; men <= en; mclr <= clr;
    end

    integer i, errors = 0;
    initial begin
        ma=0; mb=0; men=0; mclr=0; macc=0;
        #20 @(negedge clk) rst_n = 1;   // release reset away from the clock edge (recovery time)
        for (i = 0; i < 400; i = i + 1) begin
            @(negedge clk);
            a = $random; b = $random; en = ($random % 4) != 0; clr = ($random % 32) == 0;
            @(posedge clk); #(half*1.9);   // sample just before the next edge (output settled)
            if (i > 3 && acc !== macc) begin
                errors = errors + 1;
                $display("MISMATCH t=%0t acc=%0h expected=%0h", $time, acc, macc);
            end
        end
        if (errors == 0) $display("PASS: 400 cycles, no mismatch");
        else             $display("FAIL: %0d mismatches", errors);
        $finish;
    end
    `ifdef DUMP
    initial begin $dumpfile("wave.vcd"); $dumpvars(0, tb_MAC4); end
    `endif
endmodule
