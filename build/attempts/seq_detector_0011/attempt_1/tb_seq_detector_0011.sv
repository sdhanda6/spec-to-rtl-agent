`timescale 1ns/1ps

module tb_seq_detector_0011;
    reg clk;
    reg reset;
    reg data_in;
    wire detected;

    seq_detector_0011 dut (
        .clk(clk),
        .reset(reset),
        .data_in(data_in),
        .detected(detected)
    );

    initial begin
        clk = 1'd0;
        reset = 1'd0;
        data_in = 1'd0;
        #10;
        $display("PASS tb_seq_detector_0011");
        $finish;
    end
endmodule
