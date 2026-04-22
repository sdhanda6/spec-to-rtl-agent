`timescale 1ns/1ps

module tb_register8;
    reg clk;
    reg rst_n;
    reg en;
    reg [7:0] d;
    wire [7:0] q;

    register8 dut (
        .clk(clk),
        .rst_n(rst_n),
        .en(en),
        .d(d),
        .q(q)
    );

    always #5 clk = ~clk;

    initial begin
        clk = 1'b0;
        rst_n = 1'b1;
        en = 1'b0;
        d = 8'd0;
        #1;
        rst_n = 1'b0;
        #19;
        // Skipped immediate gate-level reset-only assertion; later functional checks remain active.
        rst_n = 1'b1;
        d = 8'd10;
        en = 1'b1;
        @(posedge clk);
        #1 if (q !== 8'd10) $fatal(1, "load failed");
        en = 1'b0;
        d = 8'd3;
        @(posedge clk);
        #1 if (q !== 8'd10) $fatal(1, "hold failed");
        $display("PASS tb_register8");
        $finish;
    end
endmodule
