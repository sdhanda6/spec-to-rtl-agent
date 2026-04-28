module seq_1011 (clk,
    din,
    dout,
    reset);
 input clk;
 input din;
 output dout;
 input reset;

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
 wire net1;
 wire net3;
 wire net2;
 wire \state[0] ;
 wire \state[1] ;
 wire \state[2] ;
 wire \state[3] ;
 wire clknet_0_clk;
 wire clknet_1_0__leaf_clk;
 wire clknet_1_1__leaf_clk;

 sky130_fd_sc_hd__inv_1 _16_ (.A(net2),
    .Y(_04_));
 sky130_fd_sc_hd__inv_1 _17_ (.A(\state[3] ),
    .Y(_06_));
 sky130_fd_sc_hd__inv_2 _18_ (.A(net1),
    .Y(_07_));
 sky130_fd_sc_hd__o21bai_1 _19_ (.A1(_06_),
    .A2(_07_),
    .B1_N(net3),
    .Y(_05_));
 sky130_fd_sc_hd__nand2_4 _20_ (.A(_07_),
    .B(\state[2] ),
    .Y(_08_));
 sky130_fd_sc_hd__nand2_1 _21_ (.A(\state[1] ),
    .B(net1),
    .Y(_09_));
 sky130_fd_sc_hd__nand4_1 _22_ (.A(_08_),
    .B(_09_),
    .C(\state[0] ),
    .D(_07_),
    .Y(_10_));
 sky130_fd_sc_hd__inv_1 _23_ (.A(_10_),
    .Y(_00_));
 sky130_fd_sc_hd__nand2_1 _24_ (.A(_07_),
    .B(\state[1] ),
    .Y(_11_));
 sky130_fd_sc_hd__nand2_1 _25_ (.A(_08_),
    .B(_11_),
    .Y(_01_));
 sky130_fd_sc_hd__nor2_1 _26_ (.A(\state[0] ),
    .B(\state[2] ),
    .Y(_12_));
 sky130_fd_sc_hd__nor3_1 _27_ (.A(\state[1] ),
    .B(_07_),
    .C(_12_),
    .Y(_02_));
 sky130_fd_sc_hd__nand2_1 _28_ (.A(\state[0] ),
    .B(net1),
    .Y(_13_));
 sky130_fd_sc_hd__nand2_2 _29_ (.A(_08_),
    .B(_13_),
    .Y(_14_));
 sky130_fd_sc_hd__inv_1 _30_ (.A(_09_),
    .Y(_15_));
 sky130_fd_sc_hd__o21bai_2 _31_ (.A1(_06_),
    .A2(_14_),
    .B1_N(_15_),
    .Y(_03_));
 sky130_fd_sc_hd__clkbuf_16 clkbuf_0_clk (.A(clk),
    .X(clknet_0_clk));
 sky130_fd_sc_hd__clkbuf_16 clkbuf_1_0__f_clk (.A(clknet_0_clk),
    .X(clknet_1_0__leaf_clk));
 sky130_fd_sc_hd__clkbuf_16 clkbuf_1_1__f_clk (.A(clknet_0_clk),
    .X(clknet_1_1__leaf_clk));
 sky130_fd_sc_hd__clkbuf_1 clkload0 (.A(clknet_1_0__leaf_clk));
 sky130_fd_sc_hd__dfrtp_1 \dout$_DFFE_PP0P_  (.D(_05_),
    .Q(net3),
    .RESET_B(_04_),
    .CLK(clknet_1_1__leaf_clk));
 sky130_fd_sc_hd__clkdlybuf4s50_1 input1 (.A(din),
    .X(net1));
 sky130_fd_sc_hd__clkdlybuf4s50_1 input2 (.A(reset),
    .X(net2));
 sky130_fd_sc_hd__clkdlybuf4s50_1 output3 (.A(net3),
    .X(dout));
 sky130_fd_sc_hd__dfstp_2 \state[0]$_DFF_PP1_  (.D(_00_),
    .Q(\state[0] ),
    .SET_B(_04_),
    .CLK(clknet_1_1__leaf_clk));
 sky130_fd_sc_hd__dfrtp_1 \state[1]$_DFF_PP0_  (.D(_01_),
    .Q(\state[1] ),
    .RESET_B(_04_),
    .CLK(clknet_1_0__leaf_clk));
 sky130_fd_sc_hd__dfrtp_1 \state[2]$_DFF_PP0_  (.D(_02_),
    .Q(\state[2] ),
    .RESET_B(_04_),
    .CLK(clknet_1_0__leaf_clk));
 sky130_fd_sc_hd__dfrtp_1 \state[3]$_DFF_PP0_  (.D(_03_),
    .Q(\state[3] ),
    .RESET_B(_04_),
    .CLK(clknet_1_1__leaf_clk));
endmodule
