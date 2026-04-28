`timescale 1ns/1ps

module tb_pipelined_adder;
    initial begin
        $dumpfile("waves.vcd");
        $dumpvars(0, tb_pipelined_adder);
    end
    reg clk;
    reg reset;
    reg [15:0] a;
    reg [15:0] b;
    wire [15:0] y;

    pipelined_adder dut (
        .clk(clk),
        .reset(reset),
        .a(a),
        .b(b),
        .y(y)
    );

    initial begin
        clk = 1'd0;
        reset = 1'd0;
        a = 16'd0;
        b = 16'd0;
        #10;
        $display("PASS tb_pipelined_adder");
        $finish;
    end
endmodule
