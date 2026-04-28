module pulse_latch (clk,
    flag,
    rst_n,
    set_pulse);
 input clk;
 output flag;
 input rst_n;
 input set_pulse;

 wire _0_;
 wire net3;
 wire net1;
 wire net2;

 sky130_fd_sc_hd__or2_1 _1_ (.A(net3),
    .B(net2),
    .X(_0_));
 sky130_fd_sc_hd__dfrtp_1 \flag$_DFF_PN0_  (.D(_0_),
    .Q(net3),
    .RESET_B(net1),
    .CLK(clk));
 sky130_fd_sc_hd__clkdlybuf4s50_1 input1 (.A(rst_n),
    .X(net1));
 sky130_fd_sc_hd__clkdlybuf4s50_1 input2 (.A(set_pulse),
    .X(net2));
 sky130_fd_sc_hd__clkdlybuf4s50_1 output3 (.A(net3),
    .X(flag));
endmodule
