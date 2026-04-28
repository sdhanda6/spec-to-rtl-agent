module fir_filter (clk,
    h,
    rst,
    x_in,
    y_out);
 input clk;
 input h;
 input rst;
 input x_in;
 output y_out;


 sky130_fd_sc_hd__conb_1 _2__1 (.LO(y_out));
endmodule
