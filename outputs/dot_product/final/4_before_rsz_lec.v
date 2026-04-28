module dot_product (A,
    B,
    clk,
    dot_out,
    rst,
    valid);
 input A;
 input B;
 input clk;
 output dot_out;
 input rst;
 output valid;


 sky130_fd_sc_hd__conb_1 _2__1 (.LO(dot_out));
 sky130_fd_sc_hd__conb_1 _3__2 (.LO(valid));
endmodule
