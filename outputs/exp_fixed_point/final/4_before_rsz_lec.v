module exp_fixed_point (clk,
    enable,
    exp_out,
    rst,
    x_in);
 input clk;
 input enable;
 output exp_out;
 input rst;
 input x_in;


 sky130_fd_sc_hd__conb_1 _2__1 (.LO(exp_out));
endmodule
