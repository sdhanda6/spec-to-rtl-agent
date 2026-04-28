module text_counter (clk,
    enable,
    rst_n,
    count);
 input clk;
 input enable;
 input rst_n;
 output [7:0] count;

 wire _00_;
 wire _01_;
 wire _02_;
 wire _03_;
 wire _04_;
 wire _05_;
 wire _06_;
 wire _07_;
 wire _08_;
 wire _09_;
 wire _10_;
 wire _11_;
 wire _12_;
 wire _13_;
 wire _14_;
 wire _15_;
 wire _16_;
 wire _17_;
 wire _18_;
 wire _19_;
 wire _20_;
 wire _21_;
 wire _22_;
 wire _23_;
 wire _24_;
 wire _25_;
 wire _26_;
 wire _27_;
 wire _28_;
 wire _29_;
 wire _30_;
 wire _31_;
 wire _32_;
 wire _33_;
 wire _34_;
 wire net3;
 wire net4;
 wire net5;
 wire net6;
 wire net7;
 wire net8;
 wire net9;
 wire net10;
 wire net1;
 wire net2;
 wire clknet_0_clk;
 wire clknet_1_0__leaf_clk;
 wire clknet_1_1__leaf_clk;

 sky130_fd_sc_hd__nand2_1 _35_ (.A(net6),
    .B(net5),
    .Y(_10_));
 sky130_fd_sc_hd__nand2_2 _36_ (.A(_00_),
    .B(net1),
    .Y(_11_));
 sky130_fd_sc_hd__nor2_4 _37_ (.A(_10_),
    .B(_11_),
    .Y(_12_));
 sky130_fd_sc_hd__nand2_1 _38_ (.A(net8),
    .B(net7),
    .Y(_13_));
 sky130_fd_sc_hd__inv_1 _39_ (.A(_13_),
    .Y(_14_));
 sky130_fd_sc_hd__nand2_1 _40_ (.A(_12_),
    .B(_14_),
    .Y(_15_));
 sky130_fd_sc_hd__inv_1 _41_ (.A(net9),
    .Y(_16_));
 sky130_fd_sc_hd__nand2_1 _42_ (.A(_15_),
    .B(_16_),
    .Y(_17_));
 sky130_fd_sc_hd__nand3_1 _43_ (.A(_12_),
    .B(net9),
    .C(_14_),
    .Y(_18_));
 sky130_fd_sc_hd__nand2_1 _44_ (.A(_17_),
    .B(_18_),
    .Y(_19_));
 sky130_fd_sc_hd__inv_1 _45_ (.A(_19_),
    .Y(_02_));
 sky130_fd_sc_hd__nand2_1 _46_ (.A(net5),
    .B(net4),
    .Y(_20_));
 sky130_fd_sc_hd__nand2_2 _47_ (.A(net3),
    .B(net1),
    .Y(_21_));
 sky130_fd_sc_hd__nor2_4 _48_ (.A(_20_),
    .B(_21_),
    .Y(_22_));
 sky130_fd_sc_hd__nand2_1 _49_ (.A(net6),
    .B(net7),
    .Y(_23_));
 sky130_fd_sc_hd__inv_1 _50_ (.A(_23_),
    .Y(_24_));
 sky130_fd_sc_hd__nand2_1 _51_ (.A(_22_),
    .B(_24_),
    .Y(_25_));
 sky130_fd_sc_hd__nand2_1 _52_ (.A(_25_),
    .B(net8),
    .Y(_26_));
 sky130_fd_sc_hd__nand3b_1 _53_ (.A_N(net8),
    .B(_22_),
    .C(_24_),
    .Y(_27_));
 sky130_fd_sc_hd__nand2_1 _54_ (.A(_26_),
    .B(_27_),
    .Y(_03_));
 sky130_fd_sc_hd__xor2_1 _55_ (.A(net7),
    .B(_12_),
    .X(_04_));
 sky130_fd_sc_hd__xor2_1 _56_ (.A(net6),
    .B(_22_),
    .X(_05_));
 sky130_fd_sc_hd__xnor2_1 _57_ (.A(net5),
    .B(_11_),
    .Y(_06_));
 sky130_fd_sc_hd__mux2_1 _58_ (.A0(net4),
    .A1(_01_),
    .S(net1),
    .X(_07_));
 sky130_fd_sc_hd__xor2_1 _59_ (.A(net3),
    .B(net1),
    .X(_08_));
 sky130_fd_sc_hd__nand2_1 _60_ (.A(net6),
    .B(net9),
    .Y(_28_));
 sky130_fd_sc_hd__nor2_1 _61_ (.A(_13_),
    .B(_28_),
    .Y(_29_));
 sky130_fd_sc_hd__nand2_2 _62_ (.A(_22_),
    .B(_29_),
    .Y(_30_));
 sky130_fd_sc_hd__inv_1 _63_ (.A(net10),
    .Y(_31_));
 sky130_fd_sc_hd__nand2_1 _64_ (.A(_30_),
    .B(_31_),
    .Y(_32_));
 sky130_fd_sc_hd__nand3_1 _65_ (.A(_22_),
    .B(_29_),
    .C(net10),
    .Y(_33_));
 sky130_fd_sc_hd__nand2_1 _66_ (.A(_32_),
    .B(_33_),
    .Y(_34_));
 sky130_fd_sc_hd__inv_1 _67_ (.A(_34_),
    .Y(_09_));
 sky130_fd_sc_hd__ha_1 _68_ (.A(net3),
    .B(net4),
    .COUT(_00_),
    .SUM(_01_));
 sky130_fd_sc_hd__clkbuf_16 clkbuf_0_clk (.A(clk),
    .X(clknet_0_clk));
 sky130_fd_sc_hd__clkbuf_16 clkbuf_1_0__f_clk (.A(clknet_0_clk),
    .X(clknet_1_0__leaf_clk));
 sky130_fd_sc_hd__clkbuf_16 clkbuf_1_1__f_clk (.A(clknet_0_clk),
    .X(clknet_1_1__leaf_clk));
 sky130_fd_sc_hd__dfrtp_1 \count[0]$_DFFE_PN0P_  (.D(_08_),
    .Q(net3),
    .RESET_B(net2),
    .CLK(clknet_1_0__leaf_clk));
 sky130_fd_sc_hd__dfrtp_1 \count[1]$_DFFE_PN0P_  (.D(_07_),
    .Q(net4),
    .RESET_B(net2),
    .CLK(clknet_1_0__leaf_clk));
 sky130_fd_sc_hd__dfrtp_1 \count[2]$_DFFE_PN0P_  (.D(_06_),
    .Q(net5),
    .RESET_B(net2),
    .CLK(clknet_1_0__leaf_clk));
 sky130_fd_sc_hd__dfrtp_1 \count[3]$_DFFE_PN0P_  (.D(_05_),
    .Q(net6),
    .RESET_B(net2),
    .CLK(clknet_1_0__leaf_clk));
 sky130_fd_sc_hd__dfrtp_1 \count[4]$_DFFE_PN0P_  (.D(_04_),
    .Q(net7),
    .RESET_B(net2),
    .CLK(clknet_1_1__leaf_clk));
 sky130_fd_sc_hd__dfrtp_1 \count[5]$_DFFE_PN0P_  (.D(_03_),
    .Q(net8),
    .RESET_B(net2),
    .CLK(clknet_1_1__leaf_clk));
 sky130_fd_sc_hd__dfrtp_1 \count[6]$_DFFE_PN0P_  (.D(_02_),
    .Q(net9),
    .RESET_B(net2),
    .CLK(clknet_1_1__leaf_clk));
 sky130_fd_sc_hd__dfrtp_1 \count[7]$_DFFE_PN0P_  (.D(_09_),
    .Q(net10),
    .RESET_B(net2),
    .CLK(clknet_1_1__leaf_clk));
 sky130_fd_sc_hd__clkdlybuf4s50_1 input1 (.A(enable),
    .X(net1));
 sky130_fd_sc_hd__clkdlybuf4s50_1 input2 (.A(rst_n),
    .X(net2));
 sky130_fd_sc_hd__clkdlybuf4s50_1 output10 (.A(net10),
    .X(count[7]));
 sky130_fd_sc_hd__clkdlybuf4s50_1 output3 (.A(net3),
    .X(count[0]));
 sky130_fd_sc_hd__clkdlybuf4s50_1 output4 (.A(net4),
    .X(count[1]));
 sky130_fd_sc_hd__clkdlybuf4s50_1 output5 (.A(net5),
    .X(count[2]));
 sky130_fd_sc_hd__clkdlybuf4s50_1 output6 (.A(net6),
    .X(count[3]));
 sky130_fd_sc_hd__clkdlybuf4s50_1 output7 (.A(net7),
    .X(count[4]));
 sky130_fd_sc_hd__clkdlybuf4s50_1 output8 (.A(net8),
    .X(count[5]));
 sky130_fd_sc_hd__clkdlybuf4s50_1 output9 (.A(net9),
    .X(count[6]));
endmodule
