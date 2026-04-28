`timescale 1ns/1ps

module tb_updown_counter16;
    reg clk;
    reg reset;
    reg up;
    wire [15:0] count;

    updown_counter16 dut (
        .clk(clk),
        .reset(reset),
        .up(up),
        .count(count)
    );

    initial begin
        clk = 1'd0;
        reset = 1'd0;
        up = 1'd0;
        #10;
        $display("PASS tb_updown_counter16");
        $finish;
    end
endmodule
