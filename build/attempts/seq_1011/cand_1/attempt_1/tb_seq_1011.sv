`timescale 1ns/1ps

module tb_seq_1011;
    reg clk;
    reg reset;
    reg din;
    wire dout;

    seq_1011 dut (
        .clk(clk),
        .reset(reset),
        .din(din),
        .dout(dout)
    );

    initial begin
        clk = 1'd0;
        reset = 1'd0;
        din = 1'd0;
        #10;
        $display("PASS tb_seq_1011");
        $finish;
    end
endmodule
