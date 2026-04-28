module pulse_latch (clk,
    flag,
    rst_n,
    set_pulse);
 input clk;
 output flag;
 input rst_n;
 input set_pulse;

 wire _0_;
 wire _1_;
 wire _2_;
 wire net3;
 wire net1;
 wire net2;

 sky130_fd_sc_hd__inv_1 _3_ (.A(net3),
    .Y(_1_));
 sky130_fd_sc_hd__inv_1 _4_ (.A(net2),
    .Y(_2_));
 sky130_fd_sc_hd__nand2_1 _5_ (.A(_1_),
    .B(_2_),
    .Y(_0_));
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
