`timescale 1ns/1ps

module tb_fsm_handshake;
    initial begin
        $dumpfile("waves.vcd");
        $dumpvars(0, tb_fsm_handshake);
    end
    reg clk;
    reg rst_n;
    reg start;
    reg done;
    wire busy;
    wire valid;
    localparam [1:0] IDLE = 2'd0;
    localparam [1:0] RUN = 2'd1;
    localparam [1:0] DONE = 2'd2;

    fsm_handshake dut (
        .clk(clk),
        .rst_n(rst_n),
        .start(start),
        .done(done),
        .busy(busy),
        .valid(valid)
    );

    always #5 clk = ~clk;

    reg expected_busy;
    reg expected_valid;
    task check_state_outputs;
        input [255:0] step_name;
        input integer expected_state;
        begin
            if (dut.state_q !== expected_state) begin
                $display("FAIL %0s: expected state=%0d got=%0d", step_name, expected_state, dut.state_q);
                $fatal(1);
            end
            if (busy !== expected_busy) begin
                $display("FAIL %0s: expected busy=%b got %b", step_name, expected_busy, busy);
                $fatal(1);
            end
            if (valid !== expected_valid) begin
                $display("FAIL %0s: expected valid=%b got %b", step_name, expected_valid, valid);
                $fatal(1);
            end
        end
    endtask

    initial begin
        clk = 1'b0;
        rst_n = 1'b0;
        start = 1'd0;
        done = 1'd0;
        expected_busy = 0;
        expected_valid = 0;
        #1;
        check_state_outputs("reset", IDLE);
        rst_n = 1'b1;
        start = 1'b0;
        expected_busy = 0;
        expected_valid = 0;
        @(posedge clk);
        #1 check_state_outputs("hold_idle", IDLE);
        start = 1'b1;
        expected_busy = 1;
        expected_valid = 0;
        @(posedge clk);
        #1 check_state_outputs("transition_IDLE_to_RUN", RUN);
        start = 1'b0;
        done = 1'b0;
        expected_busy = 1;
        expected_valid = 0;
        @(posedge clk);
        #1 check_state_outputs("hold_run", RUN);
        done = 1'b1;
        expected_busy = 0;
        expected_valid = 1;
        @(posedge clk);
        #1 check_state_outputs("transition_RUN_to_DONE", DONE);
        done = 1'b0;
        expected_busy = 0;
        expected_valid = 0;
        @(posedge clk);
        #1 check_state_outputs("transition_DONE_to_IDLE", IDLE);
        $display("PASS tb_fsm_handshake");
        $finish;
    end
endmodule
