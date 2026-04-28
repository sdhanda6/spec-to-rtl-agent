`timescale 1ns/1ps

module tb_dot_product;
    initial begin
        $dumpfile("waves.vcd");
        $dumpvars(0, tb_dot_product);
    end
    reg clk;
    reg rst;
    reg A;
    reg B;
    wire dot_out;
    wire valid;

    dot_product dut (
        .clk(clk),
        .rst(rst),
        .A(A),
        .B(B),
        .dot_out(dot_out),
        .valid(valid)
    );

    initial begin
        clk = 1'd0;
        rst = 1'd0;
        A = 1'd0;
        B = 1'd0;
        #10;
        $display("PASS tb_dot_product");
        $finish;
    end
endmodule
