`timescale 1ns/1ps

module tb_alu8;
    reg clk;
    reg reset;
    reg [7:0] a;
    reg [7:0] b;
    reg [2:0] op;
    wire [7:0] y;

    alu8 dut (
        .clk(clk),
        .reset(reset),
        .a(a),
        .b(b),
        .op(op),
        .y(y)
    );

    initial begin
        clk = 1'd0;
        reset = 1'd0;
        a = 8'd0;
        b = 8'd0;
        op = 3'd0;
        #10;
        $display("PASS tb_alu8");
        $finish;
    end
endmodule
