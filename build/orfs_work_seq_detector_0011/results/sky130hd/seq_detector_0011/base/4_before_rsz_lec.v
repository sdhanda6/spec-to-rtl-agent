module seq_detector_0011 (clk,
    data_in,
    detected,
    reset);
 input clk;
 input data_in;
 output detected;
 input reset;


 sky130_fd_sc_hd__conb_1 _2__1 (.LO(detected));
endmodule
