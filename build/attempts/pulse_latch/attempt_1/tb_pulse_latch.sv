`timescale 1ns/1ps

module tb_pulse_latch;
    reg clk;
    reg rst_n;
    reg set_pulse;
    wire flag;
    reg expected_flag;

    pulse_latch dut (
        .clk(clk),
        .rst_n(rst_n),
        .set_pulse(set_pulse),
        .flag(flag)
    );

    always #5 clk = ~clk;

    task check_outputs;
        input [255:0] step_name;
        begin
            if (flag !== expected_flag) begin
                $display("FAIL %0s: expected flag=%b got %b", step_name, expected_flag, flag);
                $fatal(1);
            end
        end
    endtask

    initial begin
        clk = 1'd0;
        rst_n = 1'd0;
        set_pulse = 1'd0;
        rst_n = 0;
        set_pulse = 0;
        #1;
        expected_flag = 0;
        #1 check_outputs("reset_assert");
        rst_n = 1;
        set_pulse = 1;
        @(posedge clk);
        expected_flag = 1;
        #1 check_outputs("set_flag");
        set_pulse = 0;
        @(posedge clk);
        expected_flag = 1;
        #1 check_outputs("hold_flag");
        $display("PASS tb_pulse_latch");
        $finish;
    end
endmodule
