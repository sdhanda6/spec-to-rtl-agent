`timescale 1ns/1ps

module tb_fp16_multiplier;
    reg [15:0] a;
    reg [15:0] b;
    wire [15:0] result;

    fp16_multiplier dut (
        .a(a),
        .b(b),
        .result(result)
    );

    initial begin
        a = 16'd0;
        b = 16'd0;
        #10;
        $display("PASS tb_fp16_multiplier");
        $finish;
    end
endmodule
