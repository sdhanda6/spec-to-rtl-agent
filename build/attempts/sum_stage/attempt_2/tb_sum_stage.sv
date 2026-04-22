`timescale 1ns/1ps

module tb_sum_stage;
    reg clk;
    reg rst_n;
    reg in_valid;
    reg [7:0] a;
    reg [7:0] b;
    wire [8:0] sum_out;
    reg [8:0] expected_sum_out;
    wire valid;
    reg expected_valid;

    sum_stage dut (
        .clk(clk),
        .rst_n(rst_n),
        .in_valid(in_valid),
        .a(a),
        .b(b),
        .sum_out(sum_out),
        .valid(valid)
    );

    always #5 clk = ~clk;

    task check_outputs;
        input [255:0] step_name;
        begin
            if (sum_out !== expected_sum_out) begin
                $display("FAIL %0s: expected sum_out=%b got %b", step_name, expected_sum_out, sum_out);
                $fatal(1);
            end
            if (valid !== expected_valid) begin
                $display("FAIL %0s: expected valid=%b got %b", step_name, expected_valid, valid);
                $fatal(1);
            end
        end
    endtask

    initial begin
        clk = 1'd0;
        rst_n = 1'd0;
        in_valid = 1'd0;
        a = 8'd0;
        b = 8'd0;
        rst_n = 0;
        in_valid = 0;
        a = 0;
        b = 0;
        #1;
        expected_sum_out = 0;
        expected_valid = 0;
        #1 check_outputs("reset_assert");
        rst_n = 1;
        in_valid = 1;
        a = 12;
        b = 5;
        @(posedge clk);
        expected_sum_out = 17;
        expected_valid = 1;
        #1 check_outputs("load_sum");
        in_valid = 0;
        a = 7;
        b = 8;
        @(posedge clk);
        expected_sum_out = 15;
        expected_valid = 0;
        #1 check_outputs("drop_valid_hold_sum");
        $display("PASS tb_sum_stage");
        $finish;
    end
endmodule
