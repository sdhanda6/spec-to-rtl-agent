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

 sky130_fd_sc_hd__mux2_4 _10_ (.A0(net17),
    .A1(net7),
    .S(net9),
    .X(_00_));
 sky130_fd_sc_hd__mux2_4 _11_ (.A0(net15),
    .A1(net5),
    .S(net9),
    .X(_01_));
 sky130_fd_sc_hd__mux2_4 _12_ (.A0(net14),
    .A1(net4),
    .S(net9),
    .X(_02_));
 sky130_fd_sc_hd__mux2_4 _13_ (.A0(net13),
    .A1(net3),
    .S(net9),
    .X(_03_));
 sky130_fd_sc_hd__mux2_4 _14_ (.A0(net12),
    .A1(net2),
    .S(net9),
    .X(_04_));
 sky130_fd_sc_hd__mux2_4 _15_ (.A0(net11),
    .A1(net1),
    .S(net9),
    .X(_05_));
 sky130_fd_sc_hd__mux2_4 _16_ (.A0(net18),
    .A1(net8),
    .S(net9),
    .X(_06_));
 sky130_fd_sc_hd__mux2_4 _17_ (.A0(net16),
    .A1(net6),
    .S(net9),
    .X(_07_));
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
    .CLK(clknet_1_0__leaf_clk));
 sky130_fd_sc_hd__dfrtp_1 \q[1]$_DFFE_PN0P_  (.D(_04_),
    .Q(net12),
    .RESET_B(net10),
    .CLK(clknet_1_0__leaf_clk));
 sky130_fd_sc_hd__dfrtp_1 \q[2]$_DFFE_PN0P_  (.D(_03_),
    .Q(net13),
    .RESET_B(net10),
    .CLK(clknet_1_1__leaf_clk));
 sky130_fd_sc_hd__dfrtp_1 \q[3]$_DFFE_PN0P_  (.D(_02_),
    .Q(net14),
    .RESET_B(net10),
    .CLK(clknet_1_1__leaf_clk));
 sky130_fd_sc_hd__dfrtp_1 \q[4]$_DFFE_PN0P_  (.D(_01_),
    .Q(net15),
    .RESET_B(net10),
    .CLK(clknet_1_1__leaf_clk));
 sky130_fd_sc_hd__dfrtp_1 \q[5]$_DFFE_PN0P_  (.D(_07_),
    .Q(net16),
    .RESET_B(net10),
    .CLK(clknet_1_1__leaf_clk));
 sky130_fd_sc_hd__dfrtp_1 \q[6]$_DFFE_PN0P_  (.D(_00_),
    .Q(net17),
    .RESET_B(net10),
    .CLK(clknet_1_0__leaf_clk));
 sky130_fd_sc_hd__dfrtp_1 \q[7]$_DFFE_PN0P_  (.D(_06_),
    .Q(net18),
    .RESET_B(net10),
    .CLK(clknet_1_0__leaf_clk));
endmodule
