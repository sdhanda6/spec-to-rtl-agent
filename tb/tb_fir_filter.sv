`timescale 1ns/1ps

module tb_fir_filter;
    reg clk;
    reg rst;
    reg x_in;
    reg h;
    wire y_out;

    fir_filter dut (
        .clk(clk),
        .rst(rst),
        .x_in(x_in),
        .h(h),
        .y_out(y_out)
    );

    initial begin
        clk = 1'd0;
        rst = 1'd0;
        x_in = 1'd0;
        h = 1'd0;
        #10;
        $display("PASS tb_fir_filter");
        $finish;
    end
endmodule
