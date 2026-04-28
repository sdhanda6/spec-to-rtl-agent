module register8 (clk,
    en,
    rst_n,
    d,
    q);
 input clk;
 input en;
 input rst_n;
 input [7:0] d;
 output [7:0] q;

 wire _00_;
 wire _01_;
 wire _02_;
 wire _03_;
 wire _04_;
 wire _05_;
 wire _06_;
 wire _07_;
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
 wire net1;
 wire net2;
 wire net3;
 wire net4;
 wire net5;
 wire net6;
 wire net7;
 wire net8;
 wire net9;
 wire net11;
 wire net12;
 wire net13;
 wire net14;
 wire net15;
 wire net16;
 wire net17;
 wire net18;
 wire net10;
 wire clknet_0_clk;
 wire clknet_1_0__leaf_clk;
 wire clknet_1_1__leaf_clk;

 sky130_fd_sc_hd__inv_2 _27_ (.A(net9),
    .Y(_09_));
 sky130_fd_sc_hd__nand2_1 _28_ (.A(_09_),
    .B(net17),
    .Y(_10_));
 sky130_fd_sc_hd__nand2_1 _29_ (.A(net7),
    .B(net9),
    .Y(_11_));
 sky130_fd_sc_hd__nand2_1 _30_ (.A(_10_),
    .B(_11_),
    .Y(_00_));
 sky130_fd_sc_hd__nand2_1 _31_ (.A(_09_),
    .B(net15),
    .Y(_12_));
 sky130_fd_sc_hd__nand2_1 _32_ (.A(net9),
    .B(net5),
    .Y(_13_));
 sky130_fd_sc_hd__nand2_1 _33_ (.A(_12_),
    .B(_13_),
    .Y(_01_));
 sky130_fd_sc_hd__nand2_1 _34_ (.A(_09_),
    .B(net14),
    .Y(_14_));
 sky130_fd_sc_hd__nand2_1 _35_ (.A(net9),
    .B(net4),
    .Y(_15_));
 sky130_fd_sc_hd__nand2_1 _36_ (.A(_14_),
    .B(_15_),
    .Y(_02_));
 sky130_fd_sc_hd__nand2_1 _37_ (.A(_09_),
    .B(net13),
    .Y(_16_));
 sky130_fd_sc_hd__nand2_1 _38_ (.A(net9),
    .B(net3),
    .Y(_17_));
 sky130_fd_sc_hd__nand2_1 _39_ (.A(_16_),
    .B(_17_),
    .Y(_03_));
 sky130_fd_sc_hd__nand2_1 _40_ (.A(_09_),
    .B(net12),
    .Y(_18_));
 sky130_fd_sc_hd__nand2_1 _41_ (.A(net9),
    .B(net2),
    .Y(_19_));
 sky130_fd_sc_hd__nand2_1 _42_ (.A(_18_),
    .B(_19_),
    .Y(_04_));
 sky130_fd_sc_hd__nand2_1 _43_ (.A(_09_),
    .B(net11),
    .Y(_20_));
 sky130_fd_sc_hd__nand2_1 _44_ (.A(net9),
    .B(net1),
    .Y(_21_));
 sky130_fd_sc_hd__nand2_1 _45_ (.A(_20_),
    .B(_21_),
    .Y(_05_));
 sky130_fd_sc_hd__nand2_1 _46_ (.A(_09_),
    .B(net18),
    .Y(_22_));
 sky130_fd_sc_hd__nand2_1 _47_ (.A(net9),
    .B(net8),
    .Y(_23_));
 sky130_fd_sc_hd__nand2_1 _48_ (.A(_22_),
    .B(_23_),
    .Y(_06_));
 sky130_fd_sc_hd__nand2_1 _49_ (.A(_09_),
    .B(net16),
    .Y(_24_));
 sky130_fd_sc_hd__nand2_1 _50_ (.A(net9),
    .B(net6),
    .Y(_25_));
 sky130_fd_sc_hd__nand2_1 _51_ (.A(_24_),
    .B(_25_),
    .Y(_07_));
 sky130_fd_sc_hd__clkbuf_16 clkbuf_0_clk (.A(clk),
    .X(clknet_0_clk));
 sky130_fd_sc_hd__clkbuf_16 clkbuf_1_0__f_clk (.A(clknet_0_clk),
    .X(clknet_1_0__leaf_clk));
 sky130_fd_sc_hd__clkbuf_16 clkbuf_1_1__f_clk (.A(clknet_0_clk),
    .X(clknet_1_1__leaf_clk));
 sky130_fd_sc_hd__clkdlybuf4s50_1 input1 (.A(d[0]),
    .X(net1));
 sky130_fd_sc_hd__clkdlybuf4s50_1 input10 (.A(rst_n),
    .X(net10));
 sky130_fd_sc_hd__clkdlybuf4s50_1 input2 (.A(d[1]),
    .X(net2));
 sky130_fd_sc_hd__clkdlybuf4s50_1 input3 (.A(d[2]),
    .X(net3));
 sky130_fd_sc_hd__clkdlybuf4s50_1 input4 (.A(d[3]),
    .X(net4));
 sky130_fd_sc_hd__clkdlybuf4s50_1 input5 (.A(d[4]),
    .X(net5));
 sky130_fd_sc_hd__clkdlybuf4s50_1 input6 (.A(d[5]),
    .X(net6));
 sky130_fd_sc_hd__clkdlybuf4s50_1 input7 (.A(d[6]),
    .X(net7));
 sky130_fd_sc_hd__clkdlybuf4s50_1 input8 (.A(d[7]),
    .X(net8));
 sky130_fd_sc_hd__clkdlybuf4s50_1 input9 (.A(en),
    .X(net9));
 sky130_fd_sc_hd__clkdlybuf4s50_1 output11 (.A(net11),
    .X(q[0]));
 sky130_fd_sc_hd__clkdlybuf4s50_1 output12 (.A(net12),
    .X(q[1]));
 sky130_fd_sc_hd__clkdlybuf4s50_1 output13 (.A(net13),
    .X(q[2]));
 sky130_fd_sc_hd__clkdlybuf4s50_1 output14 (.A(net14),
    .X(q[3]));
 sky130_fd_sc_hd__clkdlybuf4s50_1 output15 (.A(net15),
    .X(q[4]));
 sky130_fd_sc_hd__clkdlybuf4s50_1 output16 (.A(net16),
    .X(q[5]));
 sky130_fd_sc_hd__clkdlybuf4s50_1 output17 (.A(net17),
    .X(q[6]));
 sky130_fd_sc_hd__clkdlybuf4s50_1 output18 (.A(net18),
    .X(q[7]));
 sky130_fd_sc_hd__dfrtp_1 \q[0]$_DFFE_PN0P_  (.D(_05_),
    .Q(net11),
    .RESET_B(net10),
    .CLK(clknet_1_1__leaf_clk));
 sky130_fd_sc_hd__dfrtp_1 \q[1]$_DFFE_PN0P_  (.D(_04_),
    .Q(net12),
    .RESET_B(net10),
    .CLK(clknet_1_0__leaf_clk));
 sky130_fd_sc_hd__dfrtp_1 \q[2]$_DFFE_PN0P_  (.D(_03_),
    .Q(net13),
    .RESET_B(net10),
    .CLK(clknet_1_0__leaf_clk));
 sky130_fd_sc_hd__dfrtp_1 \q[3]$_DFFE_PN0P_  (.D(_02_),
    .Q(net14),
    .RESET_B(net10),
    .CLK(clknet_1_0__leaf_clk));
 sky130_fd_sc_hd__dfrtp_1 \q[4]$_DFFE_PN0P_  (.D(_01_),
    .Q(net15),
    .RESET_B(net10),
    .CLK(clknet_1_1__leaf_clk));
 sky130_fd_sc_hd__dfrtp_1 \q[5]$_DFFE_PN0P_  (.D(_07_),
    .Q(net16),
    .RESET_B(net10),
    .CLK(clknet_1_0__leaf_clk));
 sky130_fd_sc_hd__dfrtp_1 \q[6]$_DFFE_PN0P_  (.D(_00_),
    .Q(net17),
    .RESET_B(net10),
    .CLK(clknet_1_1__leaf_clk));
 sky130_fd_sc_hd__dfrtp_1 \q[7]$_DFFE_PN0P_  (.D(_06_),
    .Q(net18),
    .RESET_B(net10),
    .CLK(clknet_1_1__leaf_clk));
endmodule
