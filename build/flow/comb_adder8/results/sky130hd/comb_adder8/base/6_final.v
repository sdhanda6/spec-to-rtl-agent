module comb_adder8 (clk,
    reset,
    a,
    b,
    y);
 input clk;
 input reset;
 input [7:0] a;
 input [7:0] b;
 output [7:0] y;

 wire _000_;
 wire _001_;
 wire _002_;
 wire _003_;
 wire _004_;
 wire _005_;
 wire _006_;
 wire _007_;
 wire _008_;
 wire _009_;
 wire _010_;
 wire _011_;
 wire _012_;
 wire _013_;
 wire _014_;
 wire _015_;
 wire _016_;
 wire _017_;
 wire _018_;
 wire _019_;
 wire _020_;
 wire _021_;
 wire _022_;
 wire _023_;
 wire _024_;
 wire _025_;
 wire _026_;
 wire _027_;
 wire _028_;
 wire _029_;
 wire _030_;
 wire _031_;
 wire _032_;
 wire _033_;
 wire _034_;
 wire _035_;
 wire _036_;
 wire _037_;
 wire _038_;
 wire _039_;
 wire _040_;
 wire _041_;
 wire _042_;
 wire _043_;
 wire _044_;
 wire _045_;
 wire _046_;
 wire _047_;
 wire _048_;
 wire _049_;
 wire _050_;
 wire _051_;
 wire _052_;
 wire _053_;
 wire _054_;
 wire _055_;
 wire _056_;
 wire _057_;
 wire _058_;
 wire _059_;
 wire _060_;
 wire _061_;
 wire _062_;
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
 wire clknet_0_clk;
 wire clknet_1_0__leaf_clk;
 wire clknet_1_1__leaf_clk;

 sky130_fd_sc_hd__nand3_1 _063_ (.A(_019_),
    .B(_012_),
    .C(_006_),
    .Y(_021_));
 sky130_fd_sc_hd__inv_1 _064_ (.A(_018_),
    .Y(_022_));
 sky130_fd_sc_hd__nand2_1 _065_ (.A(_019_),
    .B(_015_),
    .Y(_023_));
 sky130_fd_sc_hd__nand3_2 _066_ (.A(_021_),
    .B(_022_),
    .C(_023_),
    .Y(_024_));
 sky130_fd_sc_hd__nand2_1 _067_ (.A(_009_),
    .B(_011_),
    .Y(_025_));
 sky130_fd_sc_hd__nand2_1 _068_ (.A(_017_),
    .B(_014_),
    .Y(_026_));
 sky130_fd_sc_hd__nor2_1 _069_ (.A(_025_),
    .B(_026_),
    .Y(_027_));
 sky130_fd_sc_hd__nand2_1 _070_ (.A(_024_),
    .B(_027_),
    .Y(_028_));
 sky130_fd_sc_hd__nand2_1 _071_ (.A(_017_),
    .B(_013_),
    .Y(_029_));
 sky130_fd_sc_hd__inv_1 _072_ (.A(_016_),
    .Y(_030_));
 sky130_fd_sc_hd__nand2_1 _073_ (.A(_029_),
    .B(_030_),
    .Y(_031_));
 sky130_fd_sc_hd__inv_1 _074_ (.A(_025_),
    .Y(_032_));
 sky130_fd_sc_hd__nand2_1 _075_ (.A(_009_),
    .B(_010_),
    .Y(_033_));
 sky130_fd_sc_hd__inv_1 _076_ (.A(_008_),
    .Y(_034_));
 sky130_fd_sc_hd__nand2_1 _077_ (.A(_033_),
    .B(_034_),
    .Y(_035_));
 sky130_fd_sc_hd__a21oi_1 _078_ (.A1(_031_),
    .A2(_032_),
    .B1(_035_),
    .Y(_036_));
 sky130_fd_sc_hd__nand2_1 _079_ (.A(_028_),
    .B(_036_),
    .Y(_037_));
 sky130_fd_sc_hd__xor2_1 _080_ (.A(net8),
    .B(net16),
    .X(_038_));
 sky130_fd_sc_hd__inv_1 _081_ (.A(_038_),
    .Y(_039_));
 sky130_fd_sc_hd__nand2_1 _082_ (.A(_037_),
    .B(_039_),
    .Y(_040_));
 sky130_fd_sc_hd__nand3_1 _083_ (.A(_028_),
    .B(_036_),
    .C(_038_),
    .Y(_041_));
 sky130_fd_sc_hd__nand2_1 _084_ (.A(_040_),
    .B(_041_),
    .Y(_005_));
 sky130_fd_sc_hd__nand2_1 _085_ (.A(_011_),
    .B(_017_),
    .Y(_042_));
 sky130_fd_sc_hd__nor2_1 _086_ (.A(_018_),
    .B(_013_),
    .Y(_043_));
 sky130_fd_sc_hd__nand2_1 _087_ (.A(_019_),
    .B(_007_),
    .Y(_044_));
 sky130_fd_sc_hd__nand2_1 _088_ (.A(_043_),
    .B(_044_),
    .Y(_045_));
 sky130_fd_sc_hd__or2_1 _089_ (.A(_014_),
    .B(_013_),
    .X(_046_));
 sky130_fd_sc_hd__nand3b_1 _090_ (.A_N(_042_),
    .B(_045_),
    .C(_046_),
    .Y(_047_));
 sky130_fd_sc_hd__a21oi_1 _091_ (.A1(_011_),
    .A2(_016_),
    .B1(_010_),
    .Y(_048_));
 sky130_fd_sc_hd__nand2_1 _092_ (.A(_047_),
    .B(_048_),
    .Y(_049_));
 sky130_fd_sc_hd__inv_1 _093_ (.A(_009_),
    .Y(_050_));
 sky130_fd_sc_hd__nand2_1 _094_ (.A(_049_),
    .B(_050_),
    .Y(_051_));
 sky130_fd_sc_hd__nand3_1 _095_ (.A(_047_),
    .B(_009_),
    .C(_048_),
    .Y(_052_));
 sky130_fd_sc_hd__nand2_1 _096_ (.A(_051_),
    .B(_052_),
    .Y(_004_));
 sky130_fd_sc_hd__inv_1 _097_ (.A(_026_),
    .Y(_053_));
 sky130_fd_sc_hd__nand2_1 _098_ (.A(_024_),
    .B(_053_),
    .Y(_054_));
 sky130_fd_sc_hd__inv_1 _099_ (.A(_031_),
    .Y(_055_));
 sky130_fd_sc_hd__nand2_1 _100_ (.A(_054_),
    .B(_055_),
    .Y(_056_));
 sky130_fd_sc_hd__inv_1 _101_ (.A(_011_),
    .Y(_057_));
 sky130_fd_sc_hd__nand2_1 _102_ (.A(_056_),
    .B(_057_),
    .Y(_058_));
 sky130_fd_sc_hd__nand3_1 _103_ (.A(_054_),
    .B(_011_),
    .C(_055_),
    .Y(_059_));
 sky130_fd_sc_hd__nand2_1 _104_ (.A(_058_),
    .B(_059_),
    .Y(_003_));
 sky130_fd_sc_hd__nand2_1 _105_ (.A(_045_),
    .B(_046_),
    .Y(_060_));
 sky130_fd_sc_hd__xnor2_1 _106_ (.A(_017_),
    .B(_060_),
    .Y(_002_));
 sky130_fd_sc_hd__xor2_1 _107_ (.A(_014_),
    .B(_024_),
    .X(_001_));
 sky130_fd_sc_hd__xor2_1 _108_ (.A(_019_),
    .B(_007_),
    .X(_000_));
 sky130_fd_sc_hd__inv_1 _109_ (.A(net17),
    .Y(_020_));
 sky130_fd_sc_hd__fa_1 _110_ (.A(net2),
    .B(net10),
    .CIN(_006_),
    .COUT(_007_),
    .SUM(_062_));
 sky130_fd_sc_hd__ha_1 _111_ (.A(net7),
    .B(net15),
    .COUT(_008_),
    .SUM(_009_));
 sky130_fd_sc_hd__ha_1 _112_ (.A(net6),
    .B(net14),
    .COUT(_010_),
    .SUM(_011_));
 sky130_fd_sc_hd__ha_1 _113_ (.A(net1),
    .B(net9),
    .COUT(_006_),
    .SUM(_061_));
 sky130_fd_sc_hd__ha_1 _114_ (.A(net4),
    .B(net12),
    .COUT(_013_),
    .SUM(_014_));
 sky130_fd_sc_hd__ha_1 _115_ (.A(net2),
    .B(net10),
    .COUT(_015_),
    .SUM(_012_));
 sky130_fd_sc_hd__ha_1 _116_ (.A(net5),
    .B(net13),
    .COUT(_016_),
    .SUM(_017_));
 sky130_fd_sc_hd__ha_1 _117_ (.A(net3),
    .B(net11),
    .COUT(_018_),
    .SUM(_019_));
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
 sky130_fd_sc_hd__clkdlybuf4s50_1 input17 (.A(reset),
    .X(net17));
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
 sky130_fd_sc_hd__clkdlybuf4s50_1 output18 (.A(net18),
    .X(y[0]));
 sky130_fd_sc_hd__clkdlybuf4s50_1 output19 (.A(net19),
    .X(y[1]));
 sky130_fd_sc_hd__clkdlybuf4s50_1 output20 (.A(net20),
    .X(y[2]));
 sky130_fd_sc_hd__clkdlybuf4s50_1 output21 (.A(net21),
    .X(y[3]));
 sky130_fd_sc_hd__clkdlybuf4s50_1 output22 (.A(net22),
    .X(y[4]));
 sky130_fd_sc_hd__clkdlybuf4s50_1 output23 (.A(net23),
    .X(y[5]));
 sky130_fd_sc_hd__clkdlybuf4s50_1 output24 (.A(net24),
    .X(y[6]));
 sky130_fd_sc_hd__clkdlybuf4s50_1 output25 (.A(net25),
    .X(y[7]));
 sky130_fd_sc_hd__dfrtp_1 \y[0]$_DFF_PP0_  (.D(_061_),
    .Q(net18),
    .RESET_B(_020_),
    .CLK(clknet_1_0__leaf_clk));
 sky130_fd_sc_hd__dfrtp_1 \y[1]$_DFF_PP0_  (.D(_062_),
    .Q(net19),
    .RESET_B(_020_),
    .CLK(clknet_1_0__leaf_clk));
 sky130_fd_sc_hd__dfrtp_1 \y[2]$_DFF_PP0_  (.D(_000_),
    .Q(net20),
    .RESET_B(_020_),
    .CLK(clknet_1_0__leaf_clk));
 sky130_fd_sc_hd__dfrtp_1 \y[3]$_DFF_PP0_  (.D(_001_),
    .Q(net21),
    .RESET_B(_020_),
    .CLK(clknet_1_1__leaf_clk));
 sky130_fd_sc_hd__dfrtp_1 \y[4]$_DFF_PP0_  (.D(_002_),
    .Q(net22),
    .RESET_B(_020_),
    .CLK(clknet_1_0__leaf_clk));
 sky130_fd_sc_hd__dfrtp_1 \y[5]$_DFF_PP0_  (.D(_003_),
    .Q(net23),
    .RESET_B(_020_),
    .CLK(clknet_1_1__leaf_clk));
 sky130_fd_sc_hd__dfrtp_1 \y[6]$_DFF_PP0_  (.D(_004_),
    .Q(net24),
    .RESET_B(_020_),
    .CLK(clknet_1_1__leaf_clk));
 sky130_fd_sc_hd__dfrtp_1 \y[7]$_DFF_PP0_  (.D(_005_),
    .Q(net25),
    .RESET_B(_020_),
    .CLK(clknet_1_1__leaf_clk));
endmodule
