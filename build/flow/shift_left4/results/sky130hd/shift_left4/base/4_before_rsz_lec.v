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

 sky130_fd_sc_hd__inv_2 _13_ (.A(net1),
    .Y(_04_));
 sky130_fd_sc_hd__nand2_1 _14_ (.A(_04_),
    .B(net6),
    .Y(_05_));
 sky130_fd_sc_hd__nand2_1 _15_ (.A(net5),
    .B(net1),
    .Y(_06_));
 sky130_fd_sc_hd__nand2_1 _16_ (.A(_05_),
    .B(_06_),
    .Y(_00_));
 sky130_fd_sc_hd__nand2_1 _17_ (.A(_04_),
    .B(net4),
    .Y(_07_));
 sky130_fd_sc_hd__nand2_1 _18_ (.A(net1),
    .B(net3),
    .Y(_08_));
 sky130_fd_sc_hd__nand2_1 _19_ (.A(_07_),
    .B(_08_),
    .Y(_01_));
 sky130_fd_sc_hd__nand2_1 _20_ (.A(_04_),
    .B(net7),
    .Y(_09_));
 sky130_fd_sc_hd__nand2_1 _21_ (.A(net6),
    .B(net1),
    .Y(_10_));
 sky130_fd_sc_hd__nand2_1 _22_ (.A(_09_),
    .B(_10_),
    .Y(_02_));
 sky130_fd_sc_hd__nand2_1 _23_ (.A(_04_),
    .B(net5),
    .Y(_11_));
 sky130_fd_sc_hd__nand2_1 _24_ (.A(net1),
    .B(net4),
    .Y(_12_));
 sky130_fd_sc_hd__nand2_1 _25_ (.A(_11_),
    .B(_12_),
    .Y(_03_));
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
 sky130_fd_sc_hd__dfrtp_1 \shreg[0]$_DFFE_PN0P_  (.D(_01_),
    .Q(net4),
    .RESET_B(net2),
    .CLK(clknet_1_1__leaf_clk));
 sky130_fd_sc_hd__dfrtp_1 \shreg[1]$_DFFE_PN0P_  (.D(_03_),
    .Q(net5),
    .RESET_B(net2),
    .CLK(clknet_1_0__leaf_clk));
 sky130_fd_sc_hd__dfrtp_1 \shreg[2]$_DFFE_PN0P_  (.D(_00_),
    .Q(net6),
    .RESET_B(net2),
    .CLK(clknet_1_0__leaf_clk));
 sky130_fd_sc_hd__dfrtp_1 \shreg[3]$_DFFE_PN0P_  (.D(_02_),
    .Q(net7),
    .RESET_B(net2),
    .CLK(clknet_1_1__leaf_clk));
endmodule
