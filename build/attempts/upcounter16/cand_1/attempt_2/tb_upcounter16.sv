`timescale 1ns/1ps

module tb_upcounter16;
    reg clk;
    reg rst_n;
    reg en;
    wire [15:0] count;

    upcounter16 dut (
        .clk(clk),
        .rst_n(rst_n),
        .en(en),
        .count(count)
    );

    always #5 clk = ~clk;

    initial begin
        clk = 1'b0;
        rst_n = 1'b0;
        en = 1'b0;
        #2;
        if (count !== 16'd0) $fatal(1, "reset failed");
        rst_n = 1'b1;
        en = 1'b1;
        repeat (3) @(posedge clk);
        #1 if (count !== 16'd3) $fatal(1, "increment failed");
        en = 1'b0;
        @(posedge clk);
        #1 if (count !== 16'd3) $fatal(1, "hold failed");
        $display("PASS tb_upcounter16");
        $finish;
    end
endmodule
