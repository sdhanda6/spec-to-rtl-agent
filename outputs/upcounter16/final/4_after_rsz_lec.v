module upcounter16 (clk,
    en,
    rst_n,
    count);
 input clk;
 input en;
 input rst_n;
 output [15:0] count;

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
 wire _35_;
 wire _36_;
 wire _37_;
 wire _38_;
 wire _39_;
 wire _40_;
 wire _41_;
 wire _42_;
 wire _43_;
 wire net3;
 wire net4;
 wire net5;
 wire net6;
 wire net7;
 wire net8;
 wire net9;
 wire net10;
 wire net11;
 wire net12;
 wire net13;
 wire net14;
 wire net15;
 wire net16;
 wire net17;
 wire net18;
 wire net1;
 wire net2;
 wire clknet_0_clk;
 wire clknet_1_0__leaf_clk;
 wire clknet_1_1__leaf_clk;

 sky130_fd_sc_hd__inv_1 _44_ (.A(net7),
    .Y(_18_));
 sky130_fd_sc_hd__nand4_1 _45_ (.A(net6),
    .B(net5),
    .C(net4),
    .D(net18),
    .Y(_19_));
 sky130_fd_sc_hd__nor2_1 _46_ (.A(_18_),
    .B(_19_),
    .Y(_20_));
 sky130_fd_sc_hd__inv_1 _47_ (.A(net17),
    .Y(_21_));
 sky130_fd_sc_hd__nand4_1 _48_ (.A(net12),
    .B(net11),
    .C(_00_),
    .D(net1),
    .Y(_22_));
 sky130_fd_sc_hd__nand4_2 _49_ (.A(net14),
    .B(net13),
    .C(net16),
    .D(net15),
    .Y(_23_));
 sky130_fd_sc_hd__nor3_1 _50_ (.A(_21_),
    .B(_22_),
    .C(_23_),
    .Y(_24_));
 sky130_fd_sc_hd__nand2_1 _51_ (.A(_20_),
    .B(_24_),
    .Y(_25_));
 sky130_fd_sc_hd__xnor2_1 _52_ (.A(net8),
    .B(_25_),
    .Y(_02_));
 sky130_fd_sc_hd__nand2_1 _53_ (.A(net12),
    .B(net11),
    .Y(_26_));
 sky130_fd_sc_hd__nand3_1 _54_ (.A(net3),
    .B(net10),
    .C(net1),
    .Y(_27_));
 sky130_fd_sc_hd__or4_4 _55_ (.A(_21_),
    .B(_26_),
    .C(_23_),
    .D(_27_),
    .X(_28_));
 sky130_fd_sc_hd__nor2_1 _56_ (.A(_19_),
    .B(_28_),
    .Y(_29_));
 sky130_fd_sc_hd__xnor2_1 _57_ (.A(_18_),
    .B(_29_),
    .Y(_03_));
 sky130_fd_sc_hd__nand4_1 _58_ (.A(net5),
    .B(net4),
    .C(net18),
    .D(_24_),
    .Y(_30_));
 sky130_fd_sc_hd__xnor2_1 _59_ (.A(net6),
    .B(_30_),
    .Y(_04_));
 sky130_fd_sc_hd__nand2_1 _60_ (.A(net4),
    .B(net18),
    .Y(_31_));
 sky130_fd_sc_hd__nor2_1 _61_ (.A(_31_),
    .B(_28_),
    .Y(_32_));
 sky130_fd_sc_hd__xor2_1 _62_ (.A(net5),
    .B(_32_),
    .X(_05_));
 sky130_fd_sc_hd__nand2_1 _63_ (.A(net18),
    .B(_24_),
    .Y(_33_));
 sky130_fd_sc_hd__xnor2_1 _64_ (.A(net4),
    .B(_33_),
    .Y(_06_));
 sky130_fd_sc_hd__xnor2_1 _65_ (.A(net18),
    .B(_28_),
    .Y(_07_));
 sky130_fd_sc_hd__nor2_1 _66_ (.A(_22_),
    .B(_23_),
    .Y(_34_));
 sky130_fd_sc_hd__xnor2_1 _67_ (.A(_21_),
    .B(_34_),
    .Y(_08_));
 sky130_fd_sc_hd__nor2_1 _68_ (.A(_26_),
    .B(_27_),
    .Y(_35_));
 sky130_fd_sc_hd__nand4_1 _69_ (.A(net14),
    .B(net13),
    .C(net15),
    .D(_35_),
    .Y(_36_));
 sky130_fd_sc_hd__xnor2_1 _70_ (.A(net16),
    .B(_36_),
    .Y(_09_));
 sky130_fd_sc_hd__nand2_1 _71_ (.A(net14),
    .B(net13),
    .Y(_37_));
 sky130_fd_sc_hd__nor2_1 _72_ (.A(_22_),
    .B(_37_),
    .Y(_38_));
 sky130_fd_sc_hd__xor2_1 _73_ (.A(net15),
    .B(_38_),
    .X(_10_));
 sky130_fd_sc_hd__nand2_1 _74_ (.A(net13),
    .B(_35_),
    .Y(_39_));
 sky130_fd_sc_hd__xnor2_1 _75_ (.A(net14),
    .B(_39_),
    .Y(_11_));
 sky130_fd_sc_hd__xnor2_1 _76_ (.A(net13),
    .B(_22_),
    .Y(_12_));
 sky130_fd_sc_hd__nand4_1 _77_ (.A(net3),
    .B(net11),
    .C(net10),
    .D(net1),
    .Y(_40_));
 sky130_fd_sc_hd__xnor2_1 _78_ (.A(net12),
    .B(_40_),
    .Y(_13_));
 sky130_fd_sc_hd__nand2_1 _79_ (.A(_00_),
    .B(net1),
    .Y(_41_));
 sky130_fd_sc_hd__xnor2_1 _80_ (.A(net11),
    .B(_41_),
    .Y(_14_));
 sky130_fd_sc_hd__mux2_2 _81_ (.A0(net10),
    .A1(_01_),
    .S(net1),
    .X(_15_));
 sky130_fd_sc_hd__xor2_1 _82_ (.A(net3),
    .B(net1),
    .X(_16_));
 sky130_fd_sc_hd__inv_1 _83_ (.A(net8),
    .Y(_42_));
 sky130_fd_sc_hd__nor4_4 _84_ (.A(_18_),
    .B(_42_),
    .C(_19_),
    .D(_28_),
    .Y(_43_));
 sky130_fd_sc_hd__xor2_1 _85_ (.A(net9),
    .B(_43_),
    .X(_17_));
 sky130_fd_sc_hd__ha_1 _86_ (.A(net3),
    .B(net10),
    .COUT(_00_),
    .SUM(_01_));
 sky130_fd_sc_hd__clkbuf_16 clkbuf_0_clk (.A(clk),
    .X(clknet_0_clk));
 sky130_fd_sc_hd__clkbuf_16 clkbuf_1_0__f_clk (.A(clknet_0_clk),
    .X(clknet_1_0__leaf_clk));
 sky130_fd_sc_hd__clkbuf_16 clkbuf_1_1__f_clk (.A(clknet_0_clk),
    .X(clknet_1_1__leaf_clk));
 sky130_fd_sc_hd__dfrtp_1 \count[0]$_DFFE_PN0P_  (.D(_16_),
    .Q(net3),
    .RESET_B(net2),
    .CLK(clknet_1_0__leaf_clk));
 sky130_fd_sc_hd__dfrtp_1 \count[10]$_DFFE_PN0P_  (.D(_06_),
    .Q(net4),
    .RESET_B(net2),
    .CLK(clknet_1_1__leaf_clk));
 sky130_fd_sc_hd__dfrtp_1 \count[11]$_DFFE_PN0P_  (.D(_05_),
    .Q(net5),
    .RESET_B(net2),
    .CLK(clknet_1_1__leaf_clk));
 sky130_fd_sc_hd__dfrtp_1 \count[12]$_DFFE_PN0P_  (.D(_04_),
    .Q(net6),
    .RESET_B(net2),
    .CLK(clknet_1_1__leaf_clk));
 sky130_fd_sc_hd__dfrtp_1 \count[13]$_DFFE_PN0P_  (.D(_03_),
    .Q(net7),
    .RESET_B(net2),
    .CLK(clknet_1_1__leaf_clk));
 sky130_fd_sc_hd__dfrtp_1 \count[14]$_DFFE_PN0P_  (.D(_02_),
    .Q(net8),
    .RESET_B(net2),
    .CLK(clknet_1_1__leaf_clk));
 sky130_fd_sc_hd__dfrtp_1 \count[15]$_DFFE_PN0P_  (.D(_17_),
    .Q(net9),
    .RESET_B(net2),
    .CLK(clknet_1_1__leaf_clk));
 sky130_fd_sc_hd__dfrtp_1 \count[1]$_DFFE_PN0P_  (.D(_15_),
    .Q(net10),
    .RESET_B(net2),
    .CLK(clknet_1_0__leaf_clk));
 sky130_fd_sc_hd__dfrtp_1 \count[2]$_DFFE_PN0P_  (.D(_14_),
    .Q(net11),
    .RESET_B(net2),
    .CLK(clknet_1_0__leaf_clk));
 sky130_fd_sc_hd__dfrtp_1 \count[3]$_DFFE_PN0P_  (.D(_13_),
    .Q(net12),
    .RESET_B(net2),
    .CLK(clknet_1_0__leaf_clk));
 sky130_fd_sc_hd__dfrtp_1 \count[4]$_DFFE_PN0P_  (.D(_12_),
    .Q(net13),
    .RESET_B(net2),
    .CLK(clknet_1_0__leaf_clk));
 sky130_fd_sc_hd__dfrtp_1 \count[5]$_DFFE_PN0P_  (.D(_11_),
    .Q(net14),
    .RESET_B(net2),
    .CLK(clknet_1_0__leaf_clk));
 sky130_fd_sc_hd__dfrtp_1 \count[6]$_DFFE_PN0P_  (.D(_10_),
    .Q(net15),
    .RESET_B(net2),
    .CLK(clknet_1_0__leaf_clk));
 sky130_fd_sc_hd__dfrtp_1 \count[7]$_DFFE_PN0P_  (.D(_09_),
    .Q(net16),
    .RESET_B(net2),
    .CLK(clknet_1_0__leaf_clk));
 sky130_fd_sc_hd__dfrtp_1 \count[8]$_DFFE_PN0P_  (.D(_08_),
    .Q(net17),
    .RESET_B(net2),
    .CLK(clknet_1_1__leaf_clk));
 sky130_fd_sc_hd__dfrtp_1 \count[9]$_DFFE_PN0P_  (.D(_07_),
    .Q(net18),
    .RESET_B(net2),
    .CLK(clknet_1_1__leaf_clk));
 sky130_fd_sc_hd__clkdlybuf4s50_1 input1 (.A(en),
    .X(net1));
 sky130_fd_sc_hd__clkdlybuf4s50_1 input2 (.A(rst_n),
    .X(net2));
 sky130_fd_sc_hd__clkdlybuf4s50_1 output10 (.A(net10),
    .X(count[1]));
 sky130_fd_sc_hd__clkdlybuf4s50_1 output11 (.A(net11),
    .X(count[2]));
 sky130_fd_sc_hd__clkdlybuf4s50_1 output12 (.A(net12),
    .X(count[3]));
 sky130_fd_sc_hd__clkdlybuf4s50_1 output13 (.A(net13),
    .X(count[4]));
 sky130_fd_sc_hd__clkdlybuf4s50_1 output14 (.A(net14),
    .X(count[5]));
 sky130_fd_sc_hd__clkdlybuf4s50_1 output15 (.A(net15),
    .X(count[6]));
 sky130_fd_sc_hd__clkdlybuf4s50_1 output16 (.A(net16),
    .X(count[7]));
 sky130_fd_sc_hd__clkdlybuf4s50_1 output17 (.A(net17),
    .X(count[8]));
 sky130_fd_sc_hd__clkdlybuf4s50_1 output18 (.A(net18),
    .X(count[9]));
 sky130_fd_sc_hd__clkdlybuf4s50_1 output3 (.A(net3),
    .X(count[0]));
 sky130_fd_sc_hd__clkdlybuf4s50_1 output4 (.A(net4),
    .X(count[10]));
 sky130_fd_sc_hd__clkdlybuf4s50_1 output5 (.A(net5),
    .X(count[11]));
 sky130_fd_sc_hd__clkdlybuf4s50_1 output6 (.A(net6),
    .X(count[12]));
 sky130_fd_sc_hd__clkdlybuf4s50_1 output7 (.A(net7),
    .X(count[13]));
 sky130_fd_sc_hd__clkdlybuf4s50_1 output8 (.A(net8),
    .X(count[14]));
 sky130_fd_sc_hd__clkdlybuf4s50_1 output9 (.A(net9),
    .X(count[15]));
endmodule
