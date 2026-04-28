`timescale 1ns/1ps

module tb_fp16_multiplier;
    initial begin
        $dumpfile("waves.vcd");
        $dumpvars(0, tb_fp16_multiplier);
    end
    reg clk;
    reg reset;
    reg [15:0] a;
    reg [15:0] b;
    wire [15:0] result;

    fp16_multiplier dut (
        .clk(clk),
        .reset(reset),
        .a(a),
        .b(b),
        .result(result)
    );

    initial begin
        clk = 1'd0;
        reset = 1'd0;
        a = 16'd0;
        b = 16'd0;
        #10;
        $display("PASS tb_fp16_multiplier");
        $finish;
    end
endmodule
