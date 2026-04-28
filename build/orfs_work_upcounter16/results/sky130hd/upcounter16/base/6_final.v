module upcounter16 (clk,
    en,
    rst_n,
    count);
 input clk;
 input en;
 input rst_n;
 output [15:0] count;

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
 wire _063_;
 wire _064_;
 wire _065_;
 wire _066_;
 wire _067_;
 wire _068_;
 wire _069_;
 wire _070_;
 wire _071_;
 wire _072_;
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

 sky130_fd_sc_hd__inv_1 _073_ (.A(net8),
    .Y(_024_));
 sky130_fd_sc_hd__nand2_1 _074_ (.A(net12),
    .B(net11),
    .Y(_025_));
 sky130_fd_sc_hd__nand3_1 _075_ (.A(_000_),
    .B(net14),
    .C(net13),
    .Y(_026_));
 sky130_fd_sc_hd__nor2_4 _076_ (.A(_025_),
    .B(_026_),
    .Y(_027_));
 sky130_fd_sc_hd__nand2_1 _077_ (.A(net6),
    .B(net7),
    .Y(_028_));
 sky130_fd_sc_hd__nand2_1 _078_ (.A(net5),
    .B(net4),
    .Y(_029_));
 sky130_fd_sc_hd__nor2_1 _079_ (.A(_028_),
    .B(_029_),
    .Y(_030_));
 sky130_fd_sc_hd__nand2_1 _080_ (.A(net18),
    .B(net17),
    .Y(_031_));
 sky130_fd_sc_hd__inv_1 _081_ (.A(_031_),
    .Y(_032_));
 sky130_fd_sc_hd__inv_1 _082_ (.A(net16),
    .Y(_033_));
 sky130_fd_sc_hd__nand2_2 _083_ (.A(net15),
    .B(net1),
    .Y(_034_));
 sky130_fd_sc_hd__nor2_4 _084_ (.A(_033_),
    .B(_034_),
    .Y(_035_));
 sky130_fd_sc_hd__nand4_1 _085_ (.A(_027_),
    .B(_030_),
    .C(_032_),
    .D(_035_),
    .Y(_036_));
 sky130_fd_sc_hd__nor2_1 _086_ (.A(_024_),
    .B(_036_),
    .Y(_037_));
 sky130_fd_sc_hd__nand2_1 _087_ (.A(_036_),
    .B(_024_),
    .Y(_038_));
 sky130_fd_sc_hd__inv_1 _088_ (.A(_038_),
    .Y(_039_));
 sky130_fd_sc_hd__nor2_1 _089_ (.A(_037_),
    .B(_039_),
    .Y(_002_));
 sky130_fd_sc_hd__nand4_1 _090_ (.A(net14),
    .B(net17),
    .C(net16),
    .D(net15),
    .Y(_040_));
 sky130_fd_sc_hd__inv_2 _091_ (.A(net1),
    .Y(_041_));
 sky130_fd_sc_hd__nand3_4 _092_ (.A(net3),
    .B(net11),
    .C(net10),
    .Y(_042_));
 sky130_fd_sc_hd__nor2_4 _093_ (.A(_041_),
    .B(_042_),
    .Y(_043_));
 sky130_fd_sc_hd__nand2_1 _094_ (.A(net12),
    .B(net13),
    .Y(_044_));
 sky130_fd_sc_hd__inv_1 _095_ (.A(_044_),
    .Y(_045_));
 sky130_fd_sc_hd__nand2_4 _096_ (.A(_043_),
    .B(_045_),
    .Y(_046_));
 sky130_fd_sc_hd__nor2_8 _097_ (.A(_040_),
    .B(_046_),
    .Y(_047_));
 sky130_fd_sc_hd__nand2_1 _098_ (.A(net6),
    .B(net5),
    .Y(_048_));
 sky130_fd_sc_hd__nand2_1 _099_ (.A(net4),
    .B(net18),
    .Y(_049_));
 sky130_fd_sc_hd__nor2_1 _100_ (.A(_048_),
    .B(_049_),
    .Y(_050_));
 sky130_fd_sc_hd__nand2_1 _101_ (.A(_047_),
    .B(_050_),
    .Y(_051_));
 sky130_fd_sc_hd__nand2_1 _102_ (.A(_051_),
    .B(net7),
    .Y(_052_));
 sky130_fd_sc_hd__nand3b_1 _103_ (.A_N(net7),
    .B(_047_),
    .C(_050_),
    .Y(_053_));
 sky130_fd_sc_hd__nand2_1 _104_ (.A(_052_),
    .B(_053_),
    .Y(_003_));
 sky130_fd_sc_hd__nor2_1 _105_ (.A(_029_),
    .B(_031_),
    .Y(_054_));
 sky130_fd_sc_hd__nand3_1 _106_ (.A(_027_),
    .B(_035_),
    .C(_054_),
    .Y(_055_));
 sky130_fd_sc_hd__xor2_1 _107_ (.A(net6),
    .B(_055_),
    .X(_056_));
 sky130_fd_sc_hd__inv_1 _108_ (.A(_056_),
    .Y(_004_));
 sky130_fd_sc_hd__nor2_2 _109_ (.A(_034_),
    .B(_042_),
    .Y(_057_));
 sky130_fd_sc_hd__nand2_1 _110_ (.A(net17),
    .B(net16),
    .Y(_058_));
 sky130_fd_sc_hd__nor2_1 _111_ (.A(_049_),
    .B(_058_),
    .Y(_059_));
 sky130_fd_sc_hd__inv_1 _112_ (.A(net14),
    .Y(_060_));
 sky130_fd_sc_hd__nor2_1 _113_ (.A(_060_),
    .B(_044_),
    .Y(_061_));
 sky130_fd_sc_hd__nand3_1 _114_ (.A(_057_),
    .B(_059_),
    .C(_061_),
    .Y(_062_));
 sky130_fd_sc_hd__xnor2_1 _115_ (.A(net5),
    .B(_062_),
    .Y(_005_));
 sky130_fd_sc_hd__nand2_2 _116_ (.A(_027_),
    .B(_035_),
    .Y(_063_));
 sky130_fd_sc_hd__nor2_2 _117_ (.A(_031_),
    .B(_063_),
    .Y(_064_));
 sky130_fd_sc_hd__xor2_1 _118_ (.A(net4),
    .B(_064_),
    .X(_006_));
 sky130_fd_sc_hd__xor2_2 _119_ (.A(net18),
    .B(_047_),
    .X(_007_));
 sky130_fd_sc_hd__xor2_1 _120_ (.A(net17),
    .B(_063_),
    .X(_065_));
 sky130_fd_sc_hd__inv_1 _121_ (.A(_065_),
    .Y(_008_));
 sky130_fd_sc_hd__nand2_1 _122_ (.A(_057_),
    .B(_061_),
    .Y(_066_));
 sky130_fd_sc_hd__xor2_1 _123_ (.A(_033_),
    .B(_066_),
    .X(_009_));
 sky130_fd_sc_hd__nand2_1 _124_ (.A(_027_),
    .B(net1),
    .Y(_067_));
 sky130_fd_sc_hd__xnor2_1 _125_ (.A(net15),
    .B(_067_),
    .Y(_010_));
 sky130_fd_sc_hd__xor2_1 _126_ (.A(_060_),
    .B(_046_),
    .X(_011_));
 sky130_fd_sc_hd__nand2_1 _127_ (.A(_000_),
    .B(net1),
    .Y(_068_));
 sky130_fd_sc_hd__nor2_1 _128_ (.A(_025_),
    .B(_068_),
    .Y(_069_));
 sky130_fd_sc_hd__xor2_1 _129_ (.A(net13),
    .B(_069_),
    .X(_012_));
 sky130_fd_sc_hd__xor2_1 _130_ (.A(net12),
    .B(_043_),
    .X(_013_));
 sky130_fd_sc_hd__xnor2_1 _131_ (.A(net11),
    .B(_068_),
    .Y(_014_));
 sky130_fd_sc_hd__nand2_1 _132_ (.A(_041_),
    .B(net10),
    .Y(_070_));
 sky130_fd_sc_hd__nand2_1 _133_ (.A(net1),
    .B(_001_),
    .Y(_071_));
 sky130_fd_sc_hd__nand2_1 _134_ (.A(_070_),
    .B(_071_),
    .Y(_015_));
 sky130_fd_sc_hd__xor2_1 _135_ (.A(net3),
    .B(net1),
    .X(_016_));
 sky130_fd_sc_hd__inv_1 _136_ (.A(net9),
    .Y(_072_));
 sky130_fd_sc_hd__nand2_1 _137_ (.A(net7),
    .B(net8),
    .Y(_018_));
 sky130_fd_sc_hd__nor2_1 _138_ (.A(_048_),
    .B(_018_),
    .Y(_019_));
 sky130_fd_sc_hd__nand4_2 _139_ (.A(_057_),
    .B(_059_),
    .C(_019_),
    .D(_061_),
    .Y(_020_));
 sky130_fd_sc_hd__nor2_1 _140_ (.A(_072_),
    .B(_020_),
    .Y(_021_));
 sky130_fd_sc_hd__nand2_1 _141_ (.A(_020_),
    .B(_072_),
    .Y(_022_));
 sky130_fd_sc_hd__inv_1 _142_ (.A(_022_),
    .Y(_023_));
 sky130_fd_sc_hd__nor2_1 _143_ (.A(_021_),
    .B(_023_),
    .Y(_017_));
 sky130_fd_sc_hd__ha_1 _144_ (.A(net3),
    .B(net10),
    .COUT(_000_),
    .SUM(_001_));
 sky130_fd_sc_hd__clkbuf_16 clkbuf_0_clk (.A(clk),
    .X(clknet_0_clk));
 sky130_fd_sc_hd__clkbuf_16 clkbuf_1_0__f_clk (.A(clknet_0_clk),
    .X(clknet_1_0__leaf_clk));
 sky130_fd_sc_hd__clkbuf_16 clkbuf_1_1__f_clk (.A(clknet_0_clk),
    .X(clknet_1_1__leaf_clk));
 sky130_fd_sc_hd__clkbuf_8 clkload0 (.A(clknet_1_0__leaf_clk));
 sky130_fd_sc_hd__dfrtp_1 \count[0]$_DFFE_PN0P_  (.D(_016_),
    .Q(net3),
    .RESET_B(net2),
    .CLK(clknet_1_0__leaf_clk));
 sky130_fd_sc_hd__dfrtp_1 \count[10]$_DFFE_PN0P_  (.D(_006_),
    .Q(net4),
    .RESET_B(net2),
    .CLK(clknet_1_1__leaf_clk));
 sky130_fd_sc_hd__dfrtp_1 \count[11]$_DFFE_PN0P_  (.D(_005_),
    .Q(net5),
    .RESET_B(net2),
    .CLK(clknet_1_1__leaf_clk));
 sky130_fd_sc_hd__dfrtp_1 \count[12]$_DFFE_PN0P_  (.D(_004_),
    .Q(net6),
    .RESET_B(net2),
    .CLK(clknet_1_1__leaf_clk));
 sky130_fd_sc_hd__dfrtp_1 \count[13]$_DFFE_PN0P_  (.D(_003_),
    .Q(net7),
    .RESET_B(net2),
    .CLK(clknet_1_1__leaf_clk));
 sky130_fd_sc_hd__dfrtp_1 \count[14]$_DFFE_PN0P_  (.D(_002_),
    .Q(net8),
    .RESET_B(net2),
    .CLK(clknet_1_1__leaf_clk));
 sky130_fd_sc_hd__dfrtp_1 \count[15]$_DFFE_PN0P_  (.D(_017_),
    .Q(net9),
    .RESET_B(net2),
    .CLK(clknet_1_1__leaf_clk));
 sky130_fd_sc_hd__dfrtp_1 \count[1]$_DFFE_PN0P_  (.D(_015_),
    .Q(net10),
    .RESET_B(net2),
    .CLK(clknet_1_0__leaf_clk));
 sky130_fd_sc_hd__dfrtp_1 \count[2]$_DFFE_PN0P_  (.D(_014_),
    .Q(net11),
    .RESET_B(net2),
    .CLK(clknet_1_0__leaf_clk));
 sky130_fd_sc_hd__dfrtp_1 \count[3]$_DFFE_PN0P_  (.D(_013_),
    .Q(net12),
    .RESET_B(net2),
    .CLK(clknet_1_0__leaf_clk));
 sky130_fd_sc_hd__dfrtp_1 \count[4]$_DFFE_PN0P_  (.D(_012_),
    .Q(net13),
    .RESET_B(net2),
    .CLK(clknet_1_0__leaf_clk));
 sky130_fd_sc_hd__dfrtp_1 \count[5]$_DFFE_PN0P_  (.D(_011_),
    .Q(net14),
    .RESET_B(net2),
    .CLK(clknet_1_0__leaf_clk));
 sky130_fd_sc_hd__dfrtp_1 \count[6]$_DFFE_PN0P_  (.D(_010_),
    .Q(net15),
    .RESET_B(net2),
    .CLK(clknet_1_1__leaf_clk));
 sky130_fd_sc_hd__dfrtp_1 \count[7]$_DFFE_PN0P_  (.D(_009_),
    .Q(net16),
    .RESET_B(net2),
    .CLK(clknet_1_0__leaf_clk));
 sky130_fd_sc_hd__dfrtp_1 \count[8]$_DFFE_PN0P_  (.D(_008_),
    .Q(net17),
    .RESET_B(net2),
    .CLK(clknet_1_1__leaf_clk));
 sky130_fd_sc_hd__dfrtp_1 \count[9]$_DFFE_PN0P_  (.D(_007_),
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
