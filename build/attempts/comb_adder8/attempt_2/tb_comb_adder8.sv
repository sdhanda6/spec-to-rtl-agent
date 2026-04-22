`timescale 1ns/1ps

module tb_comb_adder8;
    reg [7:0] a;
    reg [7:0] b;
    wire [7:0] y;
    reg [7:0] expected_y;

    comb_adder8 dut (
        .a(a),
        .b(b),
        .y(y)
    );

    task check_outputs;
        input [255:0] vector_name;
        begin
            if (y !== expected_y) begin
                $display("FAIL %0s: expected y=%b got %b", vector_name, expected_y, y);
                $fatal(1);
            end
        end
    endtask

    initial begin
        a = 8'd0;
        b = 8'd0;
        a = 8'd0;
        b = 8'd0;
        expected_y = a + b;
        #1 check_outputs("zeros");
        a = 8'd255;
        b = 8'd255;
        expected_y = a + b;
        #1 check_outputs("ones");
        a = 8'd1;
        b = 8'd0;
        expected_y = a + b;
        #1 check_outputs("a_hot");
        a = 8'd0;
        b = 8'd1;
        expected_y = a + b;
        #1 check_outputs("b_hot");
        $display("PASS tb_comb_adder8");
        $finish;
    end
endmodule
