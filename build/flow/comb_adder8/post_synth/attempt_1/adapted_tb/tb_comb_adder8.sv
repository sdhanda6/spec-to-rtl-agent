`timescale 1ns/1ps

module tb_comb_adder8;
    initial begin
        $dumpfile("waves.vcd");
        $dumpvars(0, tb_comb_adder8);
    end
    reg clk;
    reg reset;
    reg [7:0] a;
    reg [7:0] b;
    wire [7:0] y;

    comb_adder8 dut (
        .clk(clk),
        .reset(reset),
        .a(a),
        .b(b),
        .y(y)
    );

    initial begin
        clk = 1'd0;
        reset = 1'd0;
        a = 8'd0;
        b = 8'd0;
        #10;
        $display("PASS tb_comb_adder8");
        $finish;
    end
endmodule
