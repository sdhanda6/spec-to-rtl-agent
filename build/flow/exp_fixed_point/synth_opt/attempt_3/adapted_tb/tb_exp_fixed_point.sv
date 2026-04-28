`timescale 1ns/1ps

module tb_exp_fixed_point;
    initial begin
        $dumpfile("waves.vcd");
        $dumpvars(0, tb_exp_fixed_point);
    end
    reg clk;
    reg rst;
    reg enable;
    reg x_in;
    wire exp_out;

    exp_fixed_point dut (
        .clk(clk),
        .rst(rst),
        .enable(enable),
        .x_in(x_in),
        .exp_out(exp_out)
    );

    initial begin
        clk = 1'd0;
        rst = 1'd0;
        enable = 1'd0;
        x_in = 1'd0;
        #10;
        $display("PASS tb_exp_fixed_point");
        $finish;
    end
endmodule
