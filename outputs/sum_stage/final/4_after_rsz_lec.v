module sum_stage (clk,
    in_valid,
    rst_n,
    valid,
    a,
    b,
    sum_out);
 input clk;
 input in_valid;
 input rst_n;
 output valid;
 input [7:0] a;
 input [7:0] b;
 output [8:0] sum_out;

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
 wire _44_;
 wire _45_;
 wire _46_;
 wire net1;
 wire net2;
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
 wire net19;
 wire net20;
 wire net21;
 wire net22;
 wire net23;
 wire net24;
 wire net25;
 wire net26;
 wire net27;
 wire net28;
 wire clknet_0_clk;
 wire clknet_1_0__leaf_clk;
 wire clknet_1_1__leaf_clk;

 sky130_fd_sc_hd__a21oi_1 _47_ (.A1(_19_),
    .A2(_08_),
    .B1(_18_),
    .Y(_23_));
 sky130_fd_sc_hd__nor2b_1 _48_ (.A(_23_),
    .B_N(_10_),
    .Y(_24_));
 sky130_fd_sc_hd__nand3_1 _49_ (.A(_21_),
    .B(_12_),
    .C(_09_),
    .Y(_25_));
 sky130_fd_sc_hd__a21oi_2 _50_ (.A1(_21_),
    .A2(_11_),
    .B1(_20_),
    .Y(_26_));
 sky130_fd_sc_hd__nand2_1 _51_ (.A(_25_),
    .B(_26_),
    .Y(_27_));
 sky130_fd_sc_hd__a31oi_1 _52_ (.A1(_21_),
    .A2(_12_),
    .A3(_24_),
    .B1(_27_),
    .Y(_28_));
 sky130_fd_sc_hd__nand2_1 _53_ (.A(_17_),
    .B(_14_),
    .Y(_29_));
 sky130_fd_sc_hd__a21oi_1 _54_ (.A1(_17_),
    .A2(_13_),
    .B1(_16_),
    .Y(_30_));
 sky130_fd_sc_hd__o21ai_0 _55_ (.A1(_28_),
    .A2(_29_),
    .B1(_30_),
    .Y(_00_));
 sky130_fd_sc_hd__nand2_1 _56_ (.A(_21_),
    .B(_12_),
    .Y(_31_));
 sky130_fd_sc_hd__a211oi_1 _57_ (.A1(_15_),
    .A2(_07_),
    .B1(_22_),
    .C1(_18_),
    .Y(_32_));
 sky130_fd_sc_hd__o21ai_0 _58_ (.A1(_19_),
    .A2(_18_),
    .B1(_10_),
    .Y(_33_));
 sky130_fd_sc_hd__nor3_1 _59_ (.A(_31_),
    .B(_32_),
    .C(_33_),
    .Y(_34_));
 sky130_fd_sc_hd__nor2b_2 _60_ (.A(_17_),
    .B_N(_14_),
    .Y(_35_));
 sky130_fd_sc_hd__inv_1 _61_ (.A(_17_),
    .Y(_36_));
 sky130_fd_sc_hd__nor3_1 _62_ (.A(_36_),
    .B(_14_),
    .C(_13_),
    .Y(_37_));
 sky130_fd_sc_hd__a221o_1 _63_ (.A1(_36_),
    .A2(_13_),
    .B1(_27_),
    .B2(_35_),
    .C1(_37_),
    .X(_38_));
 sky130_fd_sc_hd__nor4_1 _64_ (.A(_36_),
    .B(_13_),
    .C(_27_),
    .D(_34_),
    .Y(_39_));
 sky130_fd_sc_hd__a211o_1 _65_ (.A1(_34_),
    .A2(_35_),
    .B1(_38_),
    .C1(_39_),
    .X(_06_));
 sky130_fd_sc_hd__xnor2_1 _66_ (.A(_14_),
    .B(_28_),
    .Y(_05_));
 sky130_fd_sc_hd__o21bai_1 _67_ (.A1(_32_),
    .A2(_33_),
    .B1_N(_09_),
    .Y(_40_));
 sky130_fd_sc_hd__a21oi_1 _68_ (.A1(_12_),
    .A2(_40_),
    .B1(_11_),
    .Y(_41_));
 sky130_fd_sc_hd__xnor2_1 _69_ (.A(_21_),
    .B(_41_),
    .Y(_04_));
 sky130_fd_sc_hd__nor2_1 _70_ (.A(_09_),
    .B(_24_),
    .Y(_42_));
 sky130_fd_sc_hd__xnor2_1 _71_ (.A(_12_),
    .B(_42_),
    .Y(_03_));
 sky130_fd_sc_hd__a21o_1 _72_ (.A1(_15_),
    .A2(_07_),
    .B1(_22_),
    .X(_43_));
 sky130_fd_sc_hd__a21oi_1 _73_ (.A1(_19_),
    .A2(_43_),
    .B1(_18_),
    .Y(_44_));
 sky130_fd_sc_hd__xnor2_1 _74_ (.A(_10_),
    .B(_44_),
    .Y(_02_));
 sky130_fd_sc_hd__xor2_1 _75_ (.A(_19_),
    .B(_08_),
    .X(_01_));
 sky130_fd_sc_hd__fa_1 _76_ (.A(net2),
    .B(net10),
    .CIN(_07_),
    .COUT(_08_),
    .SUM(_46_));
 sky130_fd_sc_hd__ha_1 _77_ (.A(net4),
    .B(net12),
    .COUT(_09_),
    .SUM(_10_));
 sky130_fd_sc_hd__ha_1 _78_ (.A(net5),
    .B(net13),
    .COUT(_11_),
    .SUM(_12_));
 sky130_fd_sc_hd__ha_1 _79_ (.A(net7),
    .B(net15),
    .COUT(_13_),
    .SUM(_14_));
 sky130_fd_sc_hd__ha_1 _80_ (.A(net8),
    .B(net16),
    .COUT(_16_),
    .SUM(_17_));
 sky130_fd_sc_hd__ha_1 _81_ (.A(net1),
    .B(net9),
    .COUT(_07_),
    .SUM(_45_));
 sky130_fd_sc_hd__ha_1 _82_ (.A(net3),
    .B(net11),
    .COUT(_18_),
    .SUM(_19_));
 sky130_fd_sc_hd__ha_1 _83_ (.A(net6),
    .B(net14),
    .COUT(_20_),
    .SUM(_21_));
 sky130_fd_sc_hd__ha_1 _84_ (.A(net2),
    .B(net10),
    .COUT(_22_),
    .SUM(_15_));
 sky130_fd_sc_hd__clkbuf_16 clkbuf_0_clk (.A(clk),
    .X(clknet_0_clk));
 sky130_fd_sc_hd__clkbuf_16 clkbuf_1_0__f_clk (.A(clknet_0_clk),
    .X(clknet_1_0__leaf_clk));
 sky130_fd_sc_hd__clkbuf_16 clkbuf_1_1__f_clk (.A(clknet_0_clk),
    .X(clknet_1_1__leaf_clk));
 sky130_fd_sc_hd__clkdlybuf4s50_1 input1 (.A(a[0]),
    .X(net1));
 sky130_fd_sc_hd__clkdlybuf4s50_1 input10 (.A(b[1]),
    .X(net10));
 sky130_fd_sc_hd__clkdlybuf4s50_1 input11 (.A(b[2]),
    .X(net11));
 sky130_fd_sc_hd__clkdlybuf4s50_1 input12 (.A(b[3]),
    .X(net12));
 sky130_fd_sc_hd__clkdlybuf4s50_1 input13 (.A(b[4]),
    .X(net13));
 sky130_fd_sc_hd__clkdlybuf4s50_1 input14 (.A(b[5]),
    .X(net14));
 sky130_fd_sc_hd__clkdlybuf4s50_1 input15 (.A(b[6]),
    .X(net15));
 sky130_fd_sc_hd__clkdlybuf4s50_1 input16 (.A(b[7]),
    .X(net16));
 sky130_fd_sc_hd__clkdlybuf4s50_1 input17 (.A(in_valid),
    .X(net17));
 sky130_fd_sc_hd__clkdlybuf4s50_1 input18 (.A(rst_n),
    .X(net18));
 sky130_fd_sc_hd__clkdlybuf4s50_1 input2 (.A(a[1]),
    .X(net2));
 sky130_fd_sc_hd__clkdlybuf4s50_1 input3 (.A(a[2]),
    .X(net3));
 sky130_fd_sc_hd__clkdlybuf4s50_1 input4 (.A(a[3]),
    .X(net4));
 sky130_fd_sc_hd__clkdlybuf4s50_1 input5 (.A(a[4]),
    .X(net5));
 sky130_fd_sc_hd__clkdlybuf4s50_1 input6 (.A(a[5]),
    .X(net6));
 sky130_fd_sc_hd__clkdlybuf4s50_1 input7 (.A(a[6]),
    .X(net7));
 sky130_fd_sc_hd__clkdlybuf4s50_1 input8 (.A(a[7]),
    .X(net8));
 sky130_fd_sc_hd__clkdlybuf4s50_1 input9 (.A(b[0]),
    .X(net9));
 sky130_fd_sc_hd__clkdlybuf4s50_1 output19 (.A(net19),
    .X(sum_out[0]));
 sky130_fd_sc_hd__clkdlybuf4s50_1 output20 (.A(net20),
    .X(sum_out[1]));
 sky130_fd_sc_hd__clkdlybuf4s50_1 output21 (.A(net21),
    .X(sum_out[2]));
 sky130_fd_sc_hd__clkdlybuf4s50_1 output22 (.A(net22),
    .X(sum_out[3]));
 sky130_fd_sc_hd__clkdlybuf4s50_1 output23 (.A(net23),
    .X(sum_out[4]));
 sky130_fd_sc_hd__clkdlybuf4s50_1 output24 (.A(net24),
    .X(sum_out[5]));
 sky130_fd_sc_hd__clkdlybuf4s50_1 output25 (.A(net25),
    .X(sum_out[6]));
 sky130_fd_sc_hd__clkdlybuf4s50_1 output26 (.A(net26),
    .X(sum_out[7]));
 sky130_fd_sc_hd__clkdlybuf4s50_1 output27 (.A(net27),
    .X(sum_out[8]));
 sky130_fd_sc_hd__clkdlybuf4s50_1 output28 (.A(net28),
    .X(valid));
 sky130_fd_sc_hd__dfrtp_1 \sum_out[0]$_DFF_PN0_  (.D(_45_),
    .Q(net19),
    .RESET_B(net18),
    .CLK(clknet_1_1__leaf_clk));
 sky130_fd_sc_hd__dfrtp_1 \sum_out[1]$_DFF_PN0_  (.D(_46_),
    .Q(net20),
    .RESET_B(net18),
    .CLK(clknet_1_1__leaf_clk));
 sky130_fd_sc_hd__dfrtp_1 \sum_out[2]$_DFF_PN0_  (.D(_01_),
    .Q(net21),
    .RESET_B(net18),
    .CLK(clknet_1_1__leaf_clk));
 sky130_fd_sc_hd__dfrtp_1 \sum_out[3]$_DFF_PN0_  (.D(_02_),
    .Q(net22),
    .RESET_B(net18),
    .CLK(clknet_1_1__leaf_clk));
 sky130_fd_sc_hd__dfrtp_1 \sum_out[4]$_DFF_PN0_  (.D(_03_),
    .Q(net23),
    .RESET_B(net18),
    .CLK(clknet_1_0__leaf_clk));
 sky130_fd_sc_hd__dfrtp_1 \sum_out[5]$_DFF_PN0_  (.D(_04_),
    .Q(net24),
    .RESET_B(net18),
    .CLK(clknet_1_0__leaf_clk));
 sky130_fd_sc_hd__dfrtp_1 \sum_out[6]$_DFF_PN0_  (.D(_05_),
    .Q(net25),
    .RESET_B(net18),
    .CLK(clknet_1_0__leaf_clk));
 sky130_fd_sc_hd__dfrtp_1 \sum_out[7]$_DFF_PN0_  (.D(_06_),
    .Q(net26),
    .RESET_B(net18),
    .CLK(clknet_1_0__leaf_clk));
 sky130_fd_sc_hd__dfrtp_1 \sum_out[8]$_DFF_PN0_  (.D(_00_),
    .Q(net27),
    .RESET_B(net18),
    .CLK(clknet_1_0__leaf_clk));
 sky130_fd_sc_hd__dfrtp_1 \valid$_DFF_PN0_  (.D(net17),
    .Q(net28),
    .RESET_B(net18),
    .CLK(clknet_1_1__leaf_clk));
endmodule
