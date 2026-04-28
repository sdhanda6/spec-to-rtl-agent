module updown_counter16 (clk,
    reset,
    up,
    count);
 input clk;
 input reset;
 input up;
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
 wire _073_;
 wire _074_;
 wire _075_;
 wire _076_;
 wire _077_;
 wire _078_;
 wire _079_;
 wire _080_;
 wire _081_;
 wire _082_;
 wire _083_;
 wire _084_;
 wire _085_;
 wire _086_;
 wire _087_;
 wire _088_;
 wire _089_;
 wire _090_;
 wire _091_;
 wire _092_;
 wire _093_;
 wire _094_;
 wire _095_;
 wire _096_;
 wire _097_;
 wire _098_;
 wire _099_;
 wire _100_;
 wire _101_;
 wire _102_;
 wire _103_;
 wire _104_;
 wire _105_;
 wire _106_;
 wire _107_;
 wire _108_;
 wire _109_;
 wire _110_;
 wire _111_;
 wire _112_;
 wire _113_;
 wire _114_;
 wire _115_;
 wire _116_;
 wire _117_;
 wire _118_;
 wire _119_;
 wire _120_;
 wire _121_;
 wire _122_;
 wire _123_;
 wire _124_;
 wire _125_;
 wire _126_;
 wire _127_;
 wire _128_;
 wire _129_;
 wire _130_;
 wire _131_;
 wire _132_;
 wire _133_;
 wire _134_;
 wire _135_;
 wire _136_;
 wire _137_;
 wire _138_;
 wire _139_;
 wire _140_;
 wire _141_;
 wire _142_;
 wire _143_;
 wire _144_;
 wire _145_;
 wire _146_;
 wire _147_;
 wire _148_;
 wire _149_;
 wire _150_;
 wire _151_;
 wire _152_;
 wire _153_;
 wire _154_;
 wire _155_;
 wire _156_;
 wire _157_;
 wire _158_;
 wire _159_;
 wire _160_;
 wire _161_;
 wire _162_;
 wire _163_;
 wire _164_;
 wire _165_;
 wire _166_;
 wire _167_;
 wire _168_;
 wire _169_;
 wire _170_;
 wire _171_;
 wire _172_;
 wire _173_;
 wire _174_;
 wire _175_;
 wire _176_;
 wire _177_;
 wire _178_;
 wire _179_;
 wire _180_;
 wire _181_;
 wire _182_;
 wire _183_;
 wire _184_;
 wire _185_;
 wire _186_;
 wire _187_;
 wire _188_;
 wire _189_;
 wire _190_;
 wire _191_;
 wire _192_;
 wire _193_;
 wire _194_;
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

 sky130_fd_sc_hd__inv_1 _195_ (.A(net3),
    .Y(_015_));
 sky130_fd_sc_hd__inv_1 _196_ (.A(net10),
    .Y(_016_));
 sky130_fd_sc_hd__nand3_1 _197_ (.A(_029_),
    .B(_033_),
    .C(net3),
    .Y(_152_));
 sky130_fd_sc_hd__inv_1 _198_ (.A(_028_),
    .Y(_153_));
 sky130_fd_sc_hd__nand2_1 _199_ (.A(_029_),
    .B(_032_),
    .Y(_154_));
 sky130_fd_sc_hd__nand3_2 _200_ (.A(_152_),
    .B(_153_),
    .C(_154_),
    .Y(_155_));
 sky130_fd_sc_hd__nand2_2 _201_ (.A(_031_),
    .B(_045_),
    .Y(_156_));
 sky130_fd_sc_hd__nand2_1 _202_ (.A(_035_),
    .B(_043_),
    .Y(_157_));
 sky130_fd_sc_hd__nor2_1 _203_ (.A(_156_),
    .B(_157_),
    .Y(_158_));
 sky130_fd_sc_hd__nand2_1 _204_ (.A(_155_),
    .B(_158_),
    .Y(_159_));
 sky130_fd_sc_hd__nand2_1 _205_ (.A(_035_),
    .B(_042_),
    .Y(_160_));
 sky130_fd_sc_hd__inv_1 _206_ (.A(_034_),
    .Y(_161_));
 sky130_fd_sc_hd__nand2_1 _207_ (.A(_160_),
    .B(_161_),
    .Y(_162_));
 sky130_fd_sc_hd__inv_2 _208_ (.A(_156_),
    .Y(_163_));
 sky130_fd_sc_hd__nand2_1 _209_ (.A(_031_),
    .B(_044_),
    .Y(_164_));
 sky130_fd_sc_hd__inv_1 _210_ (.A(_030_),
    .Y(_165_));
 sky130_fd_sc_hd__nand2_1 _211_ (.A(_164_),
    .B(_165_),
    .Y(_166_));
 sky130_fd_sc_hd__a21oi_1 _212_ (.A1(_162_),
    .A2(_163_),
    .B1(_166_),
    .Y(_167_));
 sky130_fd_sc_hd__nand2_2 _213_ (.A(_159_),
    .B(_167_),
    .Y(_168_));
 sky130_fd_sc_hd__nand2_1 _214_ (.A(_023_),
    .B(_025_),
    .Y(_169_));
 sky130_fd_sc_hd__nand2_2 _215_ (.A(_041_),
    .B(_047_),
    .Y(_170_));
 sky130_fd_sc_hd__nand2_2 _216_ (.A(_021_),
    .B(_027_),
    .Y(_171_));
 sky130_fd_sc_hd__inv_2 _217_ (.A(_171_),
    .Y(_172_));
 sky130_fd_sc_hd__nand2_1 _218_ (.A(_039_),
    .B(_037_),
    .Y(_173_));
 sky130_fd_sc_hd__inv_2 _219_ (.A(_173_),
    .Y(_174_));
 sky130_fd_sc_hd__nand2_1 _220_ (.A(_172_),
    .B(_174_),
    .Y(_175_));
 sky130_fd_sc_hd__nor3_2 _221_ (.A(_169_),
    .B(_170_),
    .C(_175_),
    .Y(_176_));
 sky130_fd_sc_hd__nand2_1 _222_ (.A(_168_),
    .B(_176_),
    .Y(_177_));
 sky130_fd_sc_hd__nand2_1 _223_ (.A(_039_),
    .B(_036_),
    .Y(_178_));
 sky130_fd_sc_hd__inv_1 _224_ (.A(_038_),
    .Y(_179_));
 sky130_fd_sc_hd__nand2_1 _225_ (.A(_178_),
    .B(_179_),
    .Y(_180_));
 sky130_fd_sc_hd__nand2_1 _226_ (.A(_180_),
    .B(_172_),
    .Y(_181_));
 sky130_fd_sc_hd__nand2_1 _227_ (.A(_021_),
    .B(_026_),
    .Y(_182_));
 sky130_fd_sc_hd__inv_1 _228_ (.A(_020_),
    .Y(_183_));
 sky130_fd_sc_hd__nand2_1 _229_ (.A(_182_),
    .B(_183_),
    .Y(_184_));
 sky130_fd_sc_hd__inv_1 _230_ (.A(_184_),
    .Y(_185_));
 sky130_fd_sc_hd__nand2_1 _231_ (.A(_181_),
    .B(_185_),
    .Y(_186_));
 sky130_fd_sc_hd__nor2_1 _232_ (.A(_169_),
    .B(_170_),
    .Y(_187_));
 sky130_fd_sc_hd__nand2_1 _233_ (.A(_041_),
    .B(_046_),
    .Y(_188_));
 sky130_fd_sc_hd__inv_1 _234_ (.A(_040_),
    .Y(_189_));
 sky130_fd_sc_hd__nand2_1 _235_ (.A(_188_),
    .B(_189_),
    .Y(_190_));
 sky130_fd_sc_hd__inv_1 _236_ (.A(_169_),
    .Y(_191_));
 sky130_fd_sc_hd__nand2_1 _237_ (.A(_190_),
    .B(_191_),
    .Y(_192_));
 sky130_fd_sc_hd__a21oi_1 _238_ (.A1(_022_),
    .A2(_025_),
    .B1(_024_),
    .Y(_193_));
 sky130_fd_sc_hd__nand2_1 _239_ (.A(_192_),
    .B(_193_),
    .Y(_194_));
 sky130_fd_sc_hd__a21oi_1 _240_ (.A1(_186_),
    .A2(_187_),
    .B1(_194_),
    .Y(_049_));
 sky130_fd_sc_hd__nand2_1 _241_ (.A(_177_),
    .B(_049_),
    .Y(_050_));
 sky130_fd_sc_hd__xor2_1 _242_ (.A(net9),
    .B(net2),
    .X(_051_));
 sky130_fd_sc_hd__nand2_1 _243_ (.A(_050_),
    .B(_051_),
    .Y(_052_));
 sky130_fd_sc_hd__inv_1 _244_ (.A(_051_),
    .Y(_053_));
 sky130_fd_sc_hd__nand3_1 _245_ (.A(_177_),
    .B(_049_),
    .C(_053_),
    .Y(_054_));
 sky130_fd_sc_hd__nand2_1 _246_ (.A(_052_),
    .B(_054_),
    .Y(_005_));
 sky130_fd_sc_hd__nand2_1 _247_ (.A(_043_),
    .B(_028_),
    .Y(_055_));
 sky130_fd_sc_hd__inv_1 _248_ (.A(_042_),
    .Y(_056_));
 sky130_fd_sc_hd__nand2_1 _249_ (.A(_055_),
    .B(_056_),
    .Y(_057_));
 sky130_fd_sc_hd__nand2_2 _250_ (.A(_045_),
    .B(_035_),
    .Y(_058_));
 sky130_fd_sc_hd__clkinv_1 _251_ (.A(_058_),
    .Y(_059_));
 sky130_fd_sc_hd__nand2_1 _252_ (.A(_045_),
    .B(_034_),
    .Y(_060_));
 sky130_fd_sc_hd__inv_1 _253_ (.A(_044_),
    .Y(_061_));
 sky130_fd_sc_hd__nand2_1 _254_ (.A(_060_),
    .B(_061_),
    .Y(_062_));
 sky130_fd_sc_hd__a21oi_1 _255_ (.A1(_057_),
    .A2(_059_),
    .B1(_062_),
    .Y(_063_));
 sky130_fd_sc_hd__inv_1 _256_ (.A(_017_),
    .Y(_064_));
 sky130_fd_sc_hd__nand4_1 _257_ (.A(_059_),
    .B(_043_),
    .C(_029_),
    .D(_064_),
    .Y(_065_));
 sky130_fd_sc_hd__nand2_1 _258_ (.A(_063_),
    .B(_065_),
    .Y(_066_));
 sky130_fd_sc_hd__nand2_1 _259_ (.A(_023_),
    .B(_041_),
    .Y(_067_));
 sky130_fd_sc_hd__nand2_2 _260_ (.A(_047_),
    .B(_021_),
    .Y(_068_));
 sky130_fd_sc_hd__nand2_1 _261_ (.A(_027_),
    .B(_039_),
    .Y(_069_));
 sky130_fd_sc_hd__inv_2 _262_ (.A(_069_),
    .Y(_070_));
 sky130_fd_sc_hd__nand2_1 _263_ (.A(_037_),
    .B(_031_),
    .Y(_071_));
 sky130_fd_sc_hd__inv_1 _264_ (.A(_071_),
    .Y(_072_));
 sky130_fd_sc_hd__nand2_1 _265_ (.A(_070_),
    .B(_072_),
    .Y(_073_));
 sky130_fd_sc_hd__nor3_2 _266_ (.A(_067_),
    .B(_068_),
    .C(_073_),
    .Y(_074_));
 sky130_fd_sc_hd__nand2_1 _267_ (.A(_066_),
    .B(_074_),
    .Y(_075_));
 sky130_fd_sc_hd__nand2_1 _268_ (.A(_037_),
    .B(_030_),
    .Y(_076_));
 sky130_fd_sc_hd__inv_1 _269_ (.A(_036_),
    .Y(_077_));
 sky130_fd_sc_hd__nand2_1 _270_ (.A(_076_),
    .B(_077_),
    .Y(_078_));
 sky130_fd_sc_hd__nand2_1 _271_ (.A(_078_),
    .B(_070_),
    .Y(_079_));
 sky130_fd_sc_hd__a21oi_1 _272_ (.A1(_027_),
    .A2(_038_),
    .B1(_026_),
    .Y(_080_));
 sky130_fd_sc_hd__nand2_1 _273_ (.A(_079_),
    .B(_080_),
    .Y(_081_));
 sky130_fd_sc_hd__nor2_1 _274_ (.A(_067_),
    .B(_068_),
    .Y(_082_));
 sky130_fd_sc_hd__nand2_1 _275_ (.A(_047_),
    .B(_020_),
    .Y(_083_));
 sky130_fd_sc_hd__inv_1 _276_ (.A(_046_),
    .Y(_084_));
 sky130_fd_sc_hd__nand2_1 _277_ (.A(_083_),
    .B(_084_),
    .Y(_085_));
 sky130_fd_sc_hd__inv_1 _278_ (.A(_067_),
    .Y(_086_));
 sky130_fd_sc_hd__nand2_1 _279_ (.A(_085_),
    .B(_086_),
    .Y(_087_));
 sky130_fd_sc_hd__a21oi_1 _280_ (.A1(_023_),
    .A2(_040_),
    .B1(_022_),
    .Y(_088_));
 sky130_fd_sc_hd__nand2_1 _281_ (.A(_087_),
    .B(_088_),
    .Y(_089_));
 sky130_fd_sc_hd__a21oi_1 _282_ (.A1(_081_),
    .A2(_082_),
    .B1(_089_),
    .Y(_090_));
 sky130_fd_sc_hd__nand2_1 _283_ (.A(_075_),
    .B(_090_),
    .Y(_091_));
 sky130_fd_sc_hd__inv_1 _284_ (.A(_025_),
    .Y(_092_));
 sky130_fd_sc_hd__nand2_1 _285_ (.A(_091_),
    .B(_092_),
    .Y(_093_));
 sky130_fd_sc_hd__nand3_1 _286_ (.A(_075_),
    .B(_090_),
    .C(_025_),
    .Y(_094_));
 sky130_fd_sc_hd__nand2_1 _287_ (.A(_093_),
    .B(_094_),
    .Y(_004_));
 sky130_fd_sc_hd__inv_1 _288_ (.A(_157_),
    .Y(_095_));
 sky130_fd_sc_hd__nand2_1 _289_ (.A(_155_),
    .B(_095_),
    .Y(_096_));
 sky130_fd_sc_hd__inv_1 _290_ (.A(_162_),
    .Y(_097_));
 sky130_fd_sc_hd__nand2_2 _291_ (.A(_096_),
    .B(_097_),
    .Y(_098_));
 sky130_fd_sc_hd__nand2_1 _292_ (.A(_163_),
    .B(_174_),
    .Y(_099_));
 sky130_fd_sc_hd__nor3_1 _293_ (.A(_170_),
    .B(_171_),
    .C(_099_),
    .Y(_100_));
 sky130_fd_sc_hd__nand2_1 _294_ (.A(_098_),
    .B(_100_),
    .Y(_101_));
 sky130_fd_sc_hd__nand2_1 _295_ (.A(_166_),
    .B(_174_),
    .Y(_102_));
 sky130_fd_sc_hd__inv_1 _296_ (.A(_180_),
    .Y(_103_));
 sky130_fd_sc_hd__nand2_1 _297_ (.A(_102_),
    .B(_103_),
    .Y(_104_));
 sky130_fd_sc_hd__nor2_1 _298_ (.A(_170_),
    .B(_171_),
    .Y(_105_));
 sky130_fd_sc_hd__inv_2 _299_ (.A(_170_),
    .Y(_106_));
 sky130_fd_sc_hd__nand2_1 _300_ (.A(_184_),
    .B(_106_),
    .Y(_107_));
 sky130_fd_sc_hd__inv_1 _301_ (.A(_190_),
    .Y(_108_));
 sky130_fd_sc_hd__nand2_1 _302_ (.A(_107_),
    .B(_108_),
    .Y(_109_));
 sky130_fd_sc_hd__a21oi_2 _303_ (.A1(_104_),
    .A2(_105_),
    .B1(_109_),
    .Y(_110_));
 sky130_fd_sc_hd__nand2_1 _304_ (.A(_101_),
    .B(_110_),
    .Y(_111_));
 sky130_fd_sc_hd__inv_1 _305_ (.A(_023_),
    .Y(_112_));
 sky130_fd_sc_hd__nand2_1 _306_ (.A(_111_),
    .B(_112_),
    .Y(_113_));
 sky130_fd_sc_hd__nand3_1 _307_ (.A(_101_),
    .B(_110_),
    .C(_023_),
    .Y(_114_));
 sky130_fd_sc_hd__nand2_1 _308_ (.A(_113_),
    .B(_114_),
    .Y(_003_));
 sky130_fd_sc_hd__nand3_1 _309_ (.A(_064_),
    .B(_043_),
    .C(_029_),
    .Y(_115_));
 sky130_fd_sc_hd__nand3_1 _310_ (.A(_115_),
    .B(_056_),
    .C(_055_),
    .Y(_116_));
 sky130_fd_sc_hd__nor2_1 _311_ (.A(_068_),
    .B(_069_),
    .Y(_117_));
 sky130_fd_sc_hd__nor2_1 _312_ (.A(_058_),
    .B(_071_),
    .Y(_118_));
 sky130_fd_sc_hd__nand3_1 _313_ (.A(_116_),
    .B(_117_),
    .C(_118_),
    .Y(_119_));
 sky130_fd_sc_hd__nor2_1 _314_ (.A(_068_),
    .B(_080_),
    .Y(_120_));
 sky130_fd_sc_hd__nor2_1 _315_ (.A(_085_),
    .B(_120_),
    .Y(_121_));
 sky130_fd_sc_hd__nand2_1 _316_ (.A(_062_),
    .B(_072_),
    .Y(_122_));
 sky130_fd_sc_hd__inv_1 _317_ (.A(_078_),
    .Y(_123_));
 sky130_fd_sc_hd__nand2_1 _318_ (.A(_122_),
    .B(_123_),
    .Y(_124_));
 sky130_fd_sc_hd__nand2_1 _319_ (.A(_124_),
    .B(_117_),
    .Y(_125_));
 sky130_fd_sc_hd__nand3_1 _320_ (.A(_119_),
    .B(_121_),
    .C(_125_),
    .Y(_126_));
 sky130_fd_sc_hd__inv_1 _321_ (.A(_041_),
    .Y(_127_));
 sky130_fd_sc_hd__nand2_1 _322_ (.A(_126_),
    .B(_127_),
    .Y(_128_));
 sky130_fd_sc_hd__nand4_1 _323_ (.A(_119_),
    .B(_121_),
    .C(_125_),
    .D(_041_),
    .Y(_129_));
 sky130_fd_sc_hd__nand2_1 _324_ (.A(_128_),
    .B(_129_),
    .Y(_002_));
 sky130_fd_sc_hd__inv_1 _325_ (.A(_175_),
    .Y(_130_));
 sky130_fd_sc_hd__nand2_1 _326_ (.A(_168_),
    .B(_130_),
    .Y(_131_));
 sky130_fd_sc_hd__inv_1 _327_ (.A(_186_),
    .Y(_132_));
 sky130_fd_sc_hd__nand2_1 _328_ (.A(_131_),
    .B(_132_),
    .Y(_133_));
 sky130_fd_sc_hd__inv_1 _329_ (.A(_047_),
    .Y(_134_));
 sky130_fd_sc_hd__nand2_1 _330_ (.A(_133_),
    .B(_134_),
    .Y(_135_));
 sky130_fd_sc_hd__nand3_1 _331_ (.A(_131_),
    .B(_047_),
    .C(_132_),
    .Y(_136_));
 sky130_fd_sc_hd__nand2_1 _332_ (.A(_135_),
    .B(_136_),
    .Y(_001_));
 sky130_fd_sc_hd__inv_1 _333_ (.A(_073_),
    .Y(_137_));
 sky130_fd_sc_hd__nand2_1 _334_ (.A(_066_),
    .B(_137_),
    .Y(_138_));
 sky130_fd_sc_hd__inv_1 _335_ (.A(_081_),
    .Y(_139_));
 sky130_fd_sc_hd__nand2_1 _336_ (.A(_138_),
    .B(_139_),
    .Y(_140_));
 sky130_fd_sc_hd__inv_1 _337_ (.A(_021_),
    .Y(_141_));
 sky130_fd_sc_hd__nand2_1 _338_ (.A(_140_),
    .B(_141_),
    .Y(_142_));
 sky130_fd_sc_hd__nand3_1 _339_ (.A(_138_),
    .B(_021_),
    .C(_139_),
    .Y(_143_));
 sky130_fd_sc_hd__nand2_1 _340_ (.A(_142_),
    .B(_143_),
    .Y(_000_));
 sky130_fd_sc_hd__inv_1 _341_ (.A(_099_),
    .Y(_144_));
 sky130_fd_sc_hd__nand2_1 _342_ (.A(_098_),
    .B(_144_),
    .Y(_145_));
 sky130_fd_sc_hd__inv_1 _343_ (.A(_104_),
    .Y(_146_));
 sky130_fd_sc_hd__nand2_1 _344_ (.A(_145_),
    .B(_146_),
    .Y(_147_));
 sky130_fd_sc_hd__inv_1 _345_ (.A(_027_),
    .Y(_148_));
 sky130_fd_sc_hd__nand2_1 _346_ (.A(_147_),
    .B(_148_),
    .Y(_149_));
 sky130_fd_sc_hd__nand3_1 _347_ (.A(_145_),
    .B(_027_),
    .C(_146_),
    .Y(_150_));
 sky130_fd_sc_hd__nand2_1 _348_ (.A(_149_),
    .B(_150_),
    .Y(_014_));
 sky130_fd_sc_hd__a21oi_1 _349_ (.A1(_116_),
    .A2(_118_),
    .B1(_124_),
    .Y(_151_));
 sky130_fd_sc_hd__xnor2_1 _350_ (.A(_039_),
    .B(_151_),
    .Y(_013_));
 sky130_fd_sc_hd__xor2_1 _351_ (.A(_037_),
    .B(_168_),
    .X(_012_));
 sky130_fd_sc_hd__xor2_1 _352_ (.A(_031_),
    .B(_066_),
    .X(_011_));
 sky130_fd_sc_hd__xor2_1 _353_ (.A(_045_),
    .B(_098_),
    .X(_010_));
 sky130_fd_sc_hd__xor2_1 _354_ (.A(_035_),
    .B(_116_),
    .X(_009_));
 sky130_fd_sc_hd__xor2_1 _355_ (.A(_043_),
    .B(_155_),
    .X(_008_));
 sky130_fd_sc_hd__xnor2_1 _356_ (.A(_029_),
    .B(_017_),
    .Y(_007_));
 sky130_fd_sc_hd__inv_1 _357_ (.A(_018_),
    .Y(_006_));
 sky130_fd_sc_hd__inv_1 _358_ (.A(net1),
    .Y(_048_));
 sky130_fd_sc_hd__inv_1 _359_ (.A(net2),
    .Y(_019_));
 sky130_fd_sc_hd__fa_1 _360_ (.A(net2),
    .B(_015_),
    .CIN(_016_),
    .COUT(_017_),
    .SUM(_018_));
 sky130_fd_sc_hd__ha_1 _361_ (.A(_019_),
    .B(net4),
    .COUT(_020_),
    .SUM(_021_));
 sky130_fd_sc_hd__ha_1 _362_ (.A(_019_),
    .B(net7),
    .COUT(_022_),
    .SUM(_023_));
 sky130_fd_sc_hd__ha_1 _363_ (.A(_019_),
    .B(net8),
    .COUT(_024_),
    .SUM(_025_));
 sky130_fd_sc_hd__ha_1 _364_ (.A(_019_),
    .B(net18),
    .COUT(_026_),
    .SUM(_027_));
 sky130_fd_sc_hd__ha_1 _365_ (.A(_019_),
    .B(net11),
    .COUT(_028_),
    .SUM(_029_));
 sky130_fd_sc_hd__ha_1 _366_ (.A(_019_),
    .B(net15),
    .COUT(_030_),
    .SUM(_031_));
 sky130_fd_sc_hd__ha_1 _367_ (.A(_019_),
    .B(net10),
    .COUT(_032_),
    .SUM(_033_));
 sky130_fd_sc_hd__ha_1 _368_ (.A(_019_),
    .B(net13),
    .COUT(_034_),
    .SUM(_035_));
 sky130_fd_sc_hd__ha_1 _369_ (.A(_019_),
    .B(net16),
    .COUT(_036_),
    .SUM(_037_));
 sky130_fd_sc_hd__ha_1 _370_ (.A(_019_),
    .B(net17),
    .COUT(_038_),
    .SUM(_039_));
 sky130_fd_sc_hd__ha_1 _371_ (.A(_019_),
    .B(net6),
    .COUT(_040_),
    .SUM(_041_));
 sky130_fd_sc_hd__ha_1 _372_ (.A(_019_),
    .B(net12),
    .COUT(_042_),
    .SUM(_043_));
 sky130_fd_sc_hd__ha_1 _373_ (.A(_019_),
    .B(net14),
    .COUT(_044_),
    .SUM(_045_));
 sky130_fd_sc_hd__ha_1 _374_ (.A(_019_),
    .B(net5),
    .COUT(_046_),
    .SUM(_047_));
 sky130_fd_sc_hd__clkbuf_16 clkbuf_0_clk (.A(clk),
    .X(clknet_0_clk));
 sky130_fd_sc_hd__clkbuf_16 clkbuf_1_0__f_clk (.A(clknet_0_clk),
    .X(clknet_1_0__leaf_clk));
 sky130_fd_sc_hd__clkbuf_16 clkbuf_1_1__f_clk (.A(clknet_0_clk),
    .X(clknet_1_1__leaf_clk));
 sky130_fd_sc_hd__dfrtp_1 \count[0]$_DFF_PP0_  (.D(_015_),
    .Q(net3),
    .RESET_B(_048_),
    .CLK(clknet_1_0__leaf_clk));
 sky130_fd_sc_hd__dfrtp_1 \count[10]$_DFF_PP0_  (.D(_000_),
    .Q(net4),
    .RESET_B(_048_),
    .CLK(clknet_1_1__leaf_clk));
 sky130_fd_sc_hd__dfrtp_1 \count[11]$_DFF_PP0_  (.D(_001_),
    .Q(net5),
    .RESET_B(_048_),
    .CLK(clknet_1_1__leaf_clk));
 sky130_fd_sc_hd__dfrtp_1 \count[12]$_DFF_PP0_  (.D(_002_),
    .Q(net6),
    .RESET_B(_048_),
    .CLK(clknet_1_0__leaf_clk));
 sky130_fd_sc_hd__dfrtp_1 \count[13]$_DFF_PP0_  (.D(_003_),
    .Q(net7),
    .RESET_B(_048_),
    .CLK(clknet_1_1__leaf_clk));
 sky130_fd_sc_hd__dfrtp_1 \count[14]$_DFF_PP0_  (.D(_004_),
    .Q(net8),
    .RESET_B(_048_),
    .CLK(clknet_1_1__leaf_clk));
 sky130_fd_sc_hd__dfrtp_1 \count[15]$_DFF_PP0_  (.D(_005_),
    .Q(net9),
    .RESET_B(_048_),
    .CLK(clknet_1_0__leaf_clk));
 sky130_fd_sc_hd__dfrtp_1 \count[1]$_DFF_PP0_  (.D(_006_),
    .Q(net10),
    .RESET_B(_048_),
    .CLK(clknet_1_0__leaf_clk));
 sky130_fd_sc_hd__dfrtp_1 \count[2]$_DFF_PP0_  (.D(_007_),
    .Q(net11),
    .RESET_B(_048_),
    .CLK(clknet_1_0__leaf_clk));
 sky130_fd_sc_hd__dfrtp_1 \count[3]$_DFF_PP0_  (.D(_008_),
    .Q(net12),
    .RESET_B(_048_),
    .CLK(clknet_1_0__leaf_clk));
 sky130_fd_sc_hd__dfrtp_1 \count[4]$_DFF_PP0_  (.D(_009_),
    .Q(net13),
    .RESET_B(_048_),
    .CLK(clknet_1_0__leaf_clk));
 sky130_fd_sc_hd__dfrtp_1 \count[5]$_DFF_PP0_  (.D(_010_),
    .Q(net14),
    .RESET_B(_048_),
    .CLK(clknet_1_1__leaf_clk));
 sky130_fd_sc_hd__dfrtp_1 \count[6]$_DFF_PP0_  (.D(_011_),
    .Q(net15),
    .RESET_B(_048_),
    .CLK(clknet_1_1__leaf_clk));
 sky130_fd_sc_hd__dfrtp_1 \count[7]$_DFF_PP0_  (.D(_012_),
    .Q(net16),
    .RESET_B(_048_),
    .CLK(clknet_1_1__leaf_clk));
 sky130_fd_sc_hd__dfrtp_1 \count[8]$_DFF_PP0_  (.D(_013_),
    .Q(net17),
    .RESET_B(_048_),
    .CLK(clknet_1_1__leaf_clk));
 sky130_fd_sc_hd__dfrtp_1 \count[9]$_DFF_PP0_  (.D(_014_),
    .Q(net18),
    .RESET_B(_048_),
    .CLK(clknet_1_0__leaf_clk));
 sky130_fd_sc_hd__clkdlybuf4s50_1 input1 (.A(reset),
    .X(net1));
 sky130_fd_sc_hd__clkdlybuf4s50_1 input2 (.A(up),
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
