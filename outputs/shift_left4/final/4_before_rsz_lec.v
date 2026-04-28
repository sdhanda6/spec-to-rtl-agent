module shift_left4 (clk,
    en,
    rst_n,
    serial_in,
    shreg);
 input clk;
 input en;
 input rst_n;
 input serial_in;
 output [3:0] shreg;

 wire _0_;
 wire _1_;
 wire _2_;
 wire _3_;
 wire net1;
 wire net2;
 wire net3;
 wire net4;
 wire net5;
 wire net6;
 wire net7;
 wire clknet_0_clk;
 wire clknet_1_0__leaf_clk;
 wire clknet_1_1__leaf_clk;

 sky130_fd_sc_hd__mux2_2 _4_ (.A0(net6),
    .A1(net5),
    .S(net1),
    .X(_0_));
 sky130_fd_sc_hd__mux2_2 _5_ (.A0(net4),
    .A1(net3),
    .S(net1),
    .X(_1_));
 sky130_fd_sc_hd__mux2_2 _6_ (.A0(net7),
    .A1(net6),
    .S(net1),
    .X(_2_));
 sky130_fd_sc_hd__mux2_2 _7_ (.A0(net5),
    .A1(net4),
    .S(net1),
    .X(_3_));
 sky130_fd_sc_hd__clkbuf_16 clkbuf_0_clk (.A(clk),
    .X(clknet_0_clk));
 sky130_fd_sc_hd__clkbuf_16 clkbuf_1_0__f_clk (.A(clknet_0_clk),
    .X(clknet_1_0__leaf_clk));
 sky130_fd_sc_hd__clkbuf_16 clkbuf_1_1__f_clk (.A(clknet_0_clk),
    .X(clknet_1_1__leaf_clk));
 sky130_fd_sc_hd__clkdlybuf4s50_1 input1 (.A(en),
    .X(net1));
 sky130_fd_sc_hd__clkdlybuf4s50_1 input2 (.A(rst_n),
    .X(net2));
 sky130_fd_sc_hd__clkdlybuf4s50_1 input3 (.A(serial_in),
    .X(net3));
 sky130_fd_sc_hd__clkdlybuf4s50_1 output4 (.A(net4),
    .X(shreg[0]));
 sky130_fd_sc_hd__clkdlybuf4s50_1 output5 (.A(net5),
    .X(shreg[1]));
 sky130_fd_sc_hd__clkdlybuf4s50_1 output6 (.A(net6),
    .X(shreg[2]));
 sky130_fd_sc_hd__clkdlybuf4s50_1 output7 (.A(net7),
    .X(shreg[3]));
 sky130_fd_sc_hd__dfrtp_1 \shreg[0]$_DFFE_PN0P_  (.D(_1_),
    .Q(net4),
    .RESET_B(net2),
    .CLK(clknet_1_0__leaf_clk));
 sky130_fd_sc_hd__dfrtp_1 \shreg[1]$_DFFE_PN0P_  (.D(_3_),
    .Q(net5),
    .RESET_B(net2),
    .CLK(clknet_1_0__leaf_clk));
 sky130_fd_sc_hd__dfrtp_1 \shreg[2]$_DFFE_PN0P_  (.D(_0_),
    .Q(net6),
    .RESET_B(net2),
    .CLK(clknet_1_1__leaf_clk));
 sky130_fd_sc_hd__dfrtp_1 \shreg[3]$_DFFE_PN0P_  (.D(_2_),
    .Q(net7),
    .RESET_B(net2),
    .CLK(clknet_1_1__leaf_clk));
endmodule
