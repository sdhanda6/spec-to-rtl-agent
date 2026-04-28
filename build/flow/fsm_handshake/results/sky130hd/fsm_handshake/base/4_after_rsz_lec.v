module fsm_handshake (busy,
    clk,
    done,
    rst_n,
    start,
    valid);
 output busy;
 input clk;
 input done;
 input rst_n;
 input start;
 output valid;

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
 wire net4;
 wire net1;
 wire net2;
 wire net3;
 wire \state_q[0] ;
 wire net5;
 wire clknet_0_clk;
 wire clknet_1_0__leaf_clk;
 wire clknet_1_1__leaf_clk;

 sky130_fd_sc_hd__inv_1 _10_ (.A(net3),
    .Y(_09_));
 sky130_fd_sc_hd__nand2_1 _11_ (.A(_09_),
    .B(\state_q[0] ),
    .Y(_03_));
 sky130_fd_sc_hd__inv_1 _12_ (.A(net5),
    .Y(_04_));
 sky130_fd_sc_hd__nand2_1 _13_ (.A(_03_),
    .B(_04_),
    .Y(_01_));
 sky130_fd_sc_hd__inv_1 _14_ (.A(net1),
    .Y(_05_));
 sky130_fd_sc_hd__nand2_1 _15_ (.A(_05_),
    .B(net4),
    .Y(_06_));
 sky130_fd_sc_hd__nand2_1 _16_ (.A(net3),
    .B(\state_q[0] ),
    .Y(_07_));
 sky130_fd_sc_hd__nand2_1 _17_ (.A(_06_),
    .B(_07_),
    .Y(_02_));
 sky130_fd_sc_hd__nand2_1 _18_ (.A(net4),
    .B(net1),
    .Y(_08_));
 sky130_fd_sc_hd__inv_1 _19_ (.A(_08_),
    .Y(_00_));
 sky130_fd_sc_hd__clkbuf_16 clkbuf_0_clk (.A(clk),
    .X(clknet_0_clk));
 sky130_fd_sc_hd__clkbuf_16 clkbuf_1_0__f_clk (.A(clknet_0_clk),
    .X(clknet_1_0__leaf_clk));
 sky130_fd_sc_hd__clkbuf_16 clkbuf_1_1__f_clk (.A(clknet_0_clk),
    .X(clknet_1_1__leaf_clk));
 sky130_fd_sc_hd__clkbuf_1 clkload0 (.A(clknet_1_1__leaf_clk));
 sky130_fd_sc_hd__clkdlybuf4s50_1 input1 (.A(done),
    .X(net1));
 sky130_fd_sc_hd__clkdlybuf4s50_1 input2 (.A(rst_n),
    .X(net2));
 sky130_fd_sc_hd__clkdlybuf4s50_1 input3 (.A(start),
    .X(net3));
 sky130_fd_sc_hd__clkdlybuf4s50_1 output4 (.A(net4),
    .X(busy));
 sky130_fd_sc_hd__clkdlybuf4s50_1 output5 (.A(net5),
    .X(valid));
 sky130_fd_sc_hd__dfstp_2 \state_q[0]$_DFF_PN1_  (.D(_01_),
    .Q(\state_q[0] ),
    .SET_B(net2),
    .CLK(clknet_1_1__leaf_clk));
 sky130_fd_sc_hd__dfrtp_1 \state_q[1]$_DFF_PN0_  (.D(_00_),
    .Q(net5),
    .RESET_B(net2),
    .CLK(clknet_1_0__leaf_clk));
 sky130_fd_sc_hd__dfrtp_1 \state_q[2]$_DFF_PN0_  (.D(_02_),
    .Q(net4),
    .RESET_B(net2),
    .CLK(clknet_1_0__leaf_clk));
endmodule
