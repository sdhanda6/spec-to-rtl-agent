`timescale 1ns/1ps

module tb_shift_left4;
    reg clk;
    reg rst_n;
    reg en;
    reg serial_in;
    wire [3:0] shreg;

    shift_left4 dut (
        .clk(clk),
        .rst_n(rst_n),
        .en(en),
        .serial_in(serial_in),
        .shreg(shreg)
    );

    always #5 clk = ~clk;

    initial begin
        clk = 1'b0;
        rst_n = 1'b0;
        serial_in = 1'b0;
        en = 1'b0;
        #2;
        if (shreg !== 4'd0) $fatal(1, "reset failed");
        rst_n = 1'b1;
        en = 1'b1;
        serial_in = 1'b1;
        @(posedge clk);
        #1 if (shreg !== 4'd1) $fatal(1, "shift failed");
        serial_in = 1'b0;
        @(posedge clk);
        #1 if (shreg !== 4'd2) $fatal(1, "shift failed");
        en = 1'b0;
        serial_in = 1'b1;
        @(posedge clk);
        #1 if (shreg !== 4'd2) $fatal(1, "hold failed");
        $display("PASS tb_shift_left4");
        $finish;
    end
endmodule
