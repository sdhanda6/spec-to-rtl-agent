`timescale 1ns/1ps

module tb_text_counter;
    reg clk;
    reg rst_n;
    reg enable;
    wire [7:0] count;
    reg [7:0] expected_count;

    text_counter dut (
        .clk(clk),
        .rst_n(rst_n),
        .enable(enable),
        .count(count)
    );

    always #5 clk = ~clk;

    task check_outputs;
        input [255:0] step_name;
        begin
            if (count !== expected_count) begin
                $display("FAIL %0s: expected count=%b got %b", step_name, expected_count, count);
                $fatal(1);
            end
        end
    endtask

    initial begin
        clk = 1'd0;
        rst_n = 1'd0;
        enable = 1'd0;
        rst_n = 0;
        enable = 0;
        #1;
        expected_count = 0;
        #1 check_outputs("reset_assert");
        enable = 1;
        rst_n = 1;
        @(posedge clk);
        expected_count = 1;
        #1 check_outputs("increment_step");
        enable = 0;
        @(posedge clk);
        expected_count = 1;
        #1 check_outputs("hold_step");
        $display("PASS tb_text_counter");
        $finish;
    end
endmodule
