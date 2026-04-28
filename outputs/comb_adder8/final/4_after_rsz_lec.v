module comb_adder8 (a,
    b,
    y);
 input [7:0] a;
 input [7:0] b;
 output [7:0] y;

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

 sky130_fd_sc_hd__xor2_1 _35_ (.A(net8),
    .B(net16),
    .X(_14_));
 sky130_fd_sc_hd__a211oi_2 _36_ (.A1(_06_),
    .A2(_00_),
    .B1(_09_),
    .C1(_12_),
    .Y(_15_));
 sky130_fd_sc_hd__o21ai_1 _37_ (.A1(_13_),
    .A2(_12_),
    .B1(_08_),
    .Y(_16_));
 sky130_fd_sc_hd__nor2_1 _38_ (.A(_15_),
    .B(_16_),
    .Y(_17_));
 sky130_fd_sc_hd__nand2_1 _39_ (.A(_03_),
    .B(_05_),
    .Y(_18_));
 sky130_fd_sc_hd__a21oi_1 _40_ (.A1(_11_),
    .A2(_07_),
    .B1(_10_),
    .Y(_19_));
 sky130_fd_sc_hd__a21oi_1 _41_ (.A1(_03_),
    .A2(_04_),
    .B1(_02_),
    .Y(_20_));
 sky130_fd_sc_hd__o21ai_0 _42_ (.A1(_18_),
    .A2(_19_),
    .B1(_20_),
    .Y(_21_));
 sky130_fd_sc_hd__a41oi_2 _43_ (.A1(_03_),
    .A2(_05_),
    .A3(_11_),
    .A4(_17_),
    .B1(_21_),
    .Y(_22_));
 sky130_fd_sc_hd__xnor2_1 _44_ (.A(_14_),
    .B(_22_),
    .Y(net24));
 sky130_fd_sc_hd__a21oi_1 _45_ (.A1(_13_),
    .A2(_01_),
    .B1(_12_),
    .Y(_23_));
 sky130_fd_sc_hd__nand2_1 _46_ (.A(_11_),
    .B(_08_),
    .Y(_24_));
 sky130_fd_sc_hd__inv_1 _47_ (.A(_10_),
    .Y(_25_));
 sky130_fd_sc_hd__nand2_1 _48_ (.A(_11_),
    .B(_07_),
    .Y(_26_));
 sky130_fd_sc_hd__o211ai_1 _49_ (.A1(_23_),
    .A2(_24_),
    .B1(_25_),
    .C1(_26_),
    .Y(_27_));
 sky130_fd_sc_hd__a21oi_1 _50_ (.A1(_05_),
    .A2(_27_),
    .B1(_04_),
    .Y(_28_));
 sky130_fd_sc_hd__xnor2_1 _51_ (.A(_03_),
    .B(_28_),
    .Y(net23));
 sky130_fd_sc_hd__o21bai_1 _52_ (.A1(_15_),
    .A2(_16_),
    .B1_N(_07_),
    .Y(_29_));
 sky130_fd_sc_hd__a21oi_1 _53_ (.A1(_11_),
    .A2(_29_),
    .B1(_10_),
    .Y(_30_));
 sky130_fd_sc_hd__xnor2_1 _54_ (.A(_05_),
    .B(_30_),
    .Y(net22));
 sky130_fd_sc_hd__nor2b_1 _55_ (.A(_23_),
    .B_N(_08_),
    .Y(_31_));
 sky130_fd_sc_hd__nor2_1 _56_ (.A(_07_),
    .B(_31_),
    .Y(_32_));
 sky130_fd_sc_hd__xnor2_1 _57_ (.A(_11_),
    .B(_32_),
    .Y(net21));
 sky130_fd_sc_hd__a21o_2 _58_ (.A1(_06_),
    .A2(_00_),
    .B1(_09_),
    .X(_33_));
 sky130_fd_sc_hd__a211oi_1 _59_ (.A1(_13_),
    .A2(_33_),
    .B1(_08_),
    .C1(_12_),
    .Y(_34_));
 sky130_fd_sc_hd__nor2_1 _60_ (.A(_17_),
    .B(_34_),
    .Y(net20));
 sky130_fd_sc_hd__xor2_1 _61_ (.A(_13_),
    .B(_01_),
    .X(net19));
 sky130_fd_sc_hd__fa_1 _62_ (.A(net2),
    .B(net10),
    .CIN(_00_),
    .COUT(_01_),
    .SUM(net18));
 sky130_fd_sc_hd__ha_1 _63_ (.A(net7),
    .B(net15),
    .COUT(_02_),
    .SUM(_03_));
 sky130_fd_sc_hd__ha_1 _64_ (.A(net6),
    .B(net14),
    .COUT(_04_),
    .SUM(_05_));
 sky130_fd_sc_hd__ha_1 _65_ (.A(net1),
    .B(net9),
    .COUT(_00_),
    .SUM(net17));
 sky130_fd_sc_hd__ha_1 _66_ (.A(net4),
    .B(net12),
    .COUT(_07_),
    .SUM(_08_));
 sky130_fd_sc_hd__ha_1 _67_ (.A(net2),
    .B(net10),
    .COUT(_09_),
    .SUM(_06_));
 sky130_fd_sc_hd__ha_1 _68_ (.A(net5),
    .B(net13),
    .COUT(_10_),
    .SUM(_11_));
 sky130_fd_sc_hd__ha_1 _69_ (.A(net3),
    .B(net11),
    .COUT(_12_),
    .SUM(_13_));
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
 sky130_fd_sc_hd__clkdlybuf4s50_1 output17 (.A(net17),
    .X(y[0]));
 sky130_fd_sc_hd__clkdlybuf4s50_1 output18 (.A(net18),
    .X(y[1]));
 sky130_fd_sc_hd__clkdlybuf4s50_1 output19 (.A(net19),
    .X(y[2]));
 sky130_fd_sc_hd__clkdlybuf4s50_1 output20 (.A(net20),
    .X(y[3]));
 sky130_fd_sc_hd__clkdlybuf4s50_1 output21 (.A(net21),
    .X(y[4]));
 sky130_fd_sc_hd__clkdlybuf4s50_1 output22 (.A(net22),
    .X(y[5]));
 sky130_fd_sc_hd__clkdlybuf4s50_1 output23 (.A(net23),
    .X(y[6]));
 sky130_fd_sc_hd__clkdlybuf4s50_1 output24 (.A(net24),
    .X(y[7]));
endmodule
