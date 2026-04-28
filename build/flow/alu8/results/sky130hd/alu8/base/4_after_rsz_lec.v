module alu8 (clk,
    reset,
    a,
    b,
    op,
    y);
 input clk;
 input reset;
 input [7:0] a;
 input [7:0] b;
 input [2:0] op;
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
 wire _078_;
 wire _079_;
 wire _080_;
 wire _082_;
 wire _083_;
 wire _084_;
 wire _085_;
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
 wire _195_;
 wire _196_;
 wire _197_;
 wire _198_;
 wire _199_;
 wire _200_;
 wire _201_;
 wire _202_;
 wire _203_;
 wire _204_;
 wire _205_;
 wire _206_;
 wire _207_;
 wire _208_;
 wire _209_;
 wire _210_;
 wire _211_;
 wire _212_;
 wire _213_;
 wire _214_;
 wire _215_;
 wire _216_;
 wire _217_;
 wire _218_;
 wire _219_;
 wire _220_;
 wire _221_;
 wire _222_;
 wire _223_;
 wire _224_;
 wire _225_;
 wire _226_;
 wire _227_;
 wire _228_;
 wire _229_;
 wire _230_;
 wire _231_;
 wire _232_;
 wire _233_;
 wire _234_;
 wire _235_;
 wire _236_;
 wire _237_;
 wire _238_;
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

 sky130_fd_sc_hd__inv_2 _239_ (.A(net19),
    .Y(_074_));
 sky130_fd_sc_hd__nor3_2 _240_ (.A(net18),
    .B(net17),
    .C(_074_),
    .Y(_075_));
 sky130_fd_sc_hd__inv_2 _241_ (.A(_075_),
    .Y(_076_));
 sky130_fd_sc_hd__nand2_1 _243_ (.A(net18),
    .B(net17),
    .Y(_078_));
 sky130_fd_sc_hd__inv_2 _244_ (.A(_078_),
    .Y(_079_));
 sky130_fd_sc_hd__nand2_2 _245_ (.A(_079_),
    .B(_074_),
    .Y(_080_));
 sky130_fd_sc_hd__o21ai_2 _247_ (.A1(_045_),
    .A2(_080_),
    .B1(_076_),
    .Y(_082_));
 sky130_fd_sc_hd__xor2_1 _248_ (.A(_056_),
    .B(_003_),
    .X(_083_));
 sky130_fd_sc_hd__inv_2 _249_ (.A(net17),
    .Y(_084_));
 sky130_fd_sc_hd__nand3_2 _250_ (.A(_084_),
    .B(_074_),
    .C(net18),
    .Y(_085_));
 sky130_fd_sc_hd__inv_2 _252_ (.A(_080_),
    .Y(_087_));
 sky130_fd_sc_hd__nor2_1 _253_ (.A(_047_),
    .B(_085_),
    .Y(_088_));
 sky130_fd_sc_hd__a211oi_2 _254_ (.A1(_083_),
    .A2(_085_),
    .B1(_087_),
    .C1(_088_),
    .Y(_089_));
 sky130_fd_sc_hd__nor3_2 _255_ (.A(net18),
    .B(_084_),
    .C(_074_),
    .Y(_090_));
 sky130_fd_sc_hd__inv_2 _256_ (.A(_090_),
    .Y(_091_));
 sky130_fd_sc_hd__o221ai_1 _257_ (.A1(_046_),
    .A2(_076_),
    .B1(_082_),
    .B2(_089_),
    .C1(_091_),
    .Y(_092_));
 sky130_fd_sc_hd__inv_1 _258_ (.A(net2),
    .Y(_000_));
 sky130_fd_sc_hd__inv_2 _259_ (.A(net18),
    .Y(_093_));
 sky130_fd_sc_hd__nor3_2 _260_ (.A(net17),
    .B(_093_),
    .C(_074_),
    .Y(_094_));
 sky130_fd_sc_hd__inv_2 _261_ (.A(_094_),
    .Y(_095_));
 sky130_fd_sc_hd__o21ai_1 _262_ (.A1(_000_),
    .A2(_091_),
    .B1(_095_),
    .Y(_096_));
 sky130_fd_sc_hd__inv_1 _263_ (.A(_096_),
    .Y(_097_));
 sky130_fd_sc_hd__nor2_1 _264_ (.A(_074_),
    .B(_078_),
    .Y(_098_));
 sky130_fd_sc_hd__inv_1 _265_ (.A(_098_),
    .Y(_099_));
 sky130_fd_sc_hd__o21ai_0 _266_ (.A1(net4),
    .A2(_095_),
    .B1(_099_),
    .Y(_100_));
 sky130_fd_sc_hd__a21oi_1 _267_ (.A1(_092_),
    .A2(_097_),
    .B1(_100_),
    .Y(_070_));
 sky130_fd_sc_hd__nand2_1 _268_ (.A(_095_),
    .B(_091_),
    .Y(_101_));
 sky130_fd_sc_hd__inv_1 _269_ (.A(_101_),
    .Y(_102_));
 sky130_fd_sc_hd__o21ai_0 _270_ (.A1(_042_),
    .A2(_085_),
    .B1(_080_),
    .Y(_103_));
 sky130_fd_sc_hd__inv_2 _271_ (.A(_085_),
    .Y(_104_));
 sky130_fd_sc_hd__a21oi_1 _272_ (.A1(_056_),
    .A2(_020_),
    .B1(_055_),
    .Y(_105_));
 sky130_fd_sc_hd__inv_1 _273_ (.A(_001_),
    .Y(_106_));
 sky130_fd_sc_hd__nand3_1 _274_ (.A(_106_),
    .B(_056_),
    .C(_016_),
    .Y(_107_));
 sky130_fd_sc_hd__nand2_1 _275_ (.A(_105_),
    .B(_107_),
    .Y(_108_));
 sky130_fd_sc_hd__xor2_1 _276_ (.A(_064_),
    .B(_108_),
    .X(_109_));
 sky130_fd_sc_hd__nor2_1 _277_ (.A(_104_),
    .B(_109_),
    .Y(_110_));
 sky130_fd_sc_hd__nor2_2 _278_ (.A(_040_),
    .B(_080_),
    .Y(_111_));
 sky130_fd_sc_hd__nor2_1 _279_ (.A(_075_),
    .B(_111_),
    .Y(_112_));
 sky130_fd_sc_hd__o21ai_2 _280_ (.A1(_103_),
    .A2(_110_),
    .B1(_112_),
    .Y(_113_));
 sky130_fd_sc_hd__o211ai_1 _281_ (.A1(_041_),
    .A2(_076_),
    .B1(_102_),
    .C1(_113_),
    .Y(_114_));
 sky130_fd_sc_hd__inv_1 _282_ (.A(net5),
    .Y(_033_));
 sky130_fd_sc_hd__inv_1 _283_ (.A(net3),
    .Y(_043_));
 sky130_fd_sc_hd__o22ai_1 _284_ (.A1(_033_),
    .A2(_095_),
    .B1(_043_),
    .B2(_091_),
    .Y(_115_));
 sky130_fd_sc_hd__inv_1 _285_ (.A(_115_),
    .Y(_116_));
 sky130_fd_sc_hd__a21oi_1 _286_ (.A1(_114_),
    .A2(_116_),
    .B1(_098_),
    .Y(_069_));
 sky130_fd_sc_hd__a21oi_1 _287_ (.A1(_064_),
    .A2(_055_),
    .B1(_063_),
    .Y(_117_));
 sky130_fd_sc_hd__inv_1 _288_ (.A(_003_),
    .Y(_118_));
 sky130_fd_sc_hd__nand3_1 _289_ (.A(_118_),
    .B(_064_),
    .C(_056_),
    .Y(_119_));
 sky130_fd_sc_hd__nand2_1 _290_ (.A(_117_),
    .B(_119_),
    .Y(_120_));
 sky130_fd_sc_hd__xor2_1 _291_ (.A(_019_),
    .B(_120_),
    .X(_121_));
 sky130_fd_sc_hd__nor2_1 _292_ (.A(_037_),
    .B(_085_),
    .Y(_122_));
 sky130_fd_sc_hd__nor2_1 _293_ (.A(_087_),
    .B(_122_),
    .Y(_123_));
 sky130_fd_sc_hd__o21ai_0 _294_ (.A1(_104_),
    .A2(_121_),
    .B1(_123_),
    .Y(_124_));
 sky130_fd_sc_hd__o211ai_1 _295_ (.A1(_035_),
    .A2(_080_),
    .B1(_076_),
    .C1(_124_),
    .Y(_125_));
 sky130_fd_sc_hd__nor2_1 _296_ (.A(_036_),
    .B(_076_),
    .Y(_126_));
 sky130_fd_sc_hd__nor2_1 _297_ (.A(_126_),
    .B(_101_),
    .Y(_127_));
 sky130_fd_sc_hd__inv_1 _298_ (.A(net6),
    .Y(_028_));
 sky130_fd_sc_hd__inv_1 _299_ (.A(net4),
    .Y(_038_));
 sky130_fd_sc_hd__o22ai_1 _300_ (.A1(_028_),
    .A2(_095_),
    .B1(_038_),
    .B2(_091_),
    .Y(_128_));
 sky130_fd_sc_hd__a21oi_1 _301_ (.A1(_125_),
    .A2(_127_),
    .B1(_128_),
    .Y(_129_));
 sky130_fd_sc_hd__nor2_1 _302_ (.A(_098_),
    .B(_129_),
    .Y(_068_));
 sky130_fd_sc_hd__nand2_1 _303_ (.A(_019_),
    .B(_064_),
    .Y(_130_));
 sky130_fd_sc_hd__or2_1 _304_ (.A(_130_),
    .B(_105_),
    .X(_131_));
 sky130_fd_sc_hd__nand2_1 _305_ (.A(_019_),
    .B(_063_),
    .Y(_132_));
 sky130_fd_sc_hd__inv_1 _306_ (.A(_018_),
    .Y(_133_));
 sky130_fd_sc_hd__nand2_1 _307_ (.A(_132_),
    .B(_133_),
    .Y(_134_));
 sky130_fd_sc_hd__inv_1 _308_ (.A(_134_),
    .Y(_135_));
 sky130_fd_sc_hd__inv_1 _309_ (.A(_130_),
    .Y(_136_));
 sky130_fd_sc_hd__nand4_1 _310_ (.A(_136_),
    .B(_056_),
    .C(_016_),
    .D(_106_),
    .Y(_137_));
 sky130_fd_sc_hd__nand3_1 _311_ (.A(_131_),
    .B(_135_),
    .C(_137_),
    .Y(_138_));
 sky130_fd_sc_hd__inv_1 _312_ (.A(_015_),
    .Y(_139_));
 sky130_fd_sc_hd__nand2_1 _313_ (.A(_138_),
    .B(_139_),
    .Y(_140_));
 sky130_fd_sc_hd__nand4_1 _314_ (.A(_131_),
    .B(_137_),
    .C(_015_),
    .D(_135_),
    .Y(_141_));
 sky130_fd_sc_hd__nand3_1 _315_ (.A(_140_),
    .B(_141_),
    .C(_085_),
    .Y(_142_));
 sky130_fd_sc_hd__nor2_1 _316_ (.A(_032_),
    .B(_085_),
    .Y(_143_));
 sky130_fd_sc_hd__nor2_1 _317_ (.A(_087_),
    .B(_143_),
    .Y(_144_));
 sky130_fd_sc_hd__nand2_1 _318_ (.A(_142_),
    .B(_144_),
    .Y(_145_));
 sky130_fd_sc_hd__nor2_1 _319_ (.A(_030_),
    .B(_080_),
    .Y(_146_));
 sky130_fd_sc_hd__nor2_1 _320_ (.A(_075_),
    .B(_146_),
    .Y(_147_));
 sky130_fd_sc_hd__nand2_1 _321_ (.A(_145_),
    .B(_147_),
    .Y(_148_));
 sky130_fd_sc_hd__nor2_1 _322_ (.A(_031_),
    .B(_076_),
    .Y(_149_));
 sky130_fd_sc_hd__nor2_1 _323_ (.A(_149_),
    .B(_101_),
    .Y(_150_));
 sky130_fd_sc_hd__inv_1 _324_ (.A(net7),
    .Y(_023_));
 sky130_fd_sc_hd__o22ai_1 _325_ (.A1(_033_),
    .A2(_091_),
    .B1(_023_),
    .B2(_095_),
    .Y(_151_));
 sky130_fd_sc_hd__a21oi_1 _326_ (.A1(_148_),
    .A2(_150_),
    .B1(_151_),
    .Y(_152_));
 sky130_fd_sc_hd__nor2_1 _327_ (.A(_098_),
    .B(_152_),
    .Y(_067_));
 sky130_fd_sc_hd__nand2_1 _328_ (.A(_015_),
    .B(_019_),
    .Y(_153_));
 sky130_fd_sc_hd__or2_2 _329_ (.A(_153_),
    .B(_117_),
    .X(_154_));
 sky130_fd_sc_hd__a21oi_1 _330_ (.A1(_015_),
    .A2(_018_),
    .B1(_014_),
    .Y(_155_));
 sky130_fd_sc_hd__inv_1 _331_ (.A(_153_),
    .Y(_156_));
 sky130_fd_sc_hd__nand4_1 _332_ (.A(_156_),
    .B(_064_),
    .C(_056_),
    .D(_118_),
    .Y(_157_));
 sky130_fd_sc_hd__nand3_1 _333_ (.A(_154_),
    .B(_155_),
    .C(_157_),
    .Y(_158_));
 sky130_fd_sc_hd__inv_1 _334_ (.A(_008_),
    .Y(_159_));
 sky130_fd_sc_hd__nand2_1 _335_ (.A(_158_),
    .B(_159_),
    .Y(_160_));
 sky130_fd_sc_hd__nand4_1 _336_ (.A(_154_),
    .B(_008_),
    .C(_155_),
    .D(_157_),
    .Y(_161_));
 sky130_fd_sc_hd__nand3_1 _337_ (.A(_160_),
    .B(_161_),
    .C(_085_),
    .Y(_162_));
 sky130_fd_sc_hd__nor2_1 _338_ (.A(_027_),
    .B(_085_),
    .Y(_163_));
 sky130_fd_sc_hd__nor2_1 _339_ (.A(_087_),
    .B(_163_),
    .Y(_164_));
 sky130_fd_sc_hd__nand2_1 _340_ (.A(_162_),
    .B(_164_),
    .Y(_165_));
 sky130_fd_sc_hd__nor2_1 _341_ (.A(_025_),
    .B(_080_),
    .Y(_166_));
 sky130_fd_sc_hd__nor2_1 _342_ (.A(_075_),
    .B(_166_),
    .Y(_167_));
 sky130_fd_sc_hd__nand2_1 _343_ (.A(_165_),
    .B(_167_),
    .Y(_168_));
 sky130_fd_sc_hd__nor2_1 _344_ (.A(_026_),
    .B(_076_),
    .Y(_169_));
 sky130_fd_sc_hd__nor2_1 _345_ (.A(_169_),
    .B(_101_),
    .Y(_170_));
 sky130_fd_sc_hd__inv_1 _346_ (.A(net8),
    .Y(_057_));
 sky130_fd_sc_hd__o22ai_1 _347_ (.A1(_028_),
    .A2(_091_),
    .B1(_057_),
    .B2(_095_),
    .Y(_171_));
 sky130_fd_sc_hd__a21oi_1 _348_ (.A1(_168_),
    .A2(_170_),
    .B1(_171_),
    .Y(_172_));
 sky130_fd_sc_hd__nor2_1 _349_ (.A(_098_),
    .B(_172_),
    .Y(_066_));
 sky130_fd_sc_hd__inv_1 _350_ (.A(net11),
    .Y(_044_));
 sky130_fd_sc_hd__inv_1 _351_ (.A(net10),
    .Y(_009_));
 sky130_fd_sc_hd__inv_1 _352_ (.A(net9),
    .Y(_010_));
 sky130_fd_sc_hd__inv_1 _353_ (.A(net13),
    .Y(_034_));
 sky130_fd_sc_hd__inv_1 _354_ (.A(net14),
    .Y(_029_));
 sky130_fd_sc_hd__inv_1 _355_ (.A(net15),
    .Y(_024_));
 sky130_fd_sc_hd__nand3_2 _356_ (.A(_093_),
    .B(_074_),
    .C(net17),
    .Y(_173_));
 sky130_fd_sc_hd__inv_1 _357_ (.A(_011_),
    .Y(_174_));
 sky130_fd_sc_hd__nand2_1 _358_ (.A(_173_),
    .B(_174_),
    .Y(_175_));
 sky130_fd_sc_hd__xor2_1 _359_ (.A(_044_),
    .B(_175_),
    .X(_176_));
 sky130_fd_sc_hd__inv_1 _360_ (.A(_176_),
    .Y(_054_));
 sky130_fd_sc_hd__inv_1 _361_ (.A(net1),
    .Y(_021_));
 sky130_fd_sc_hd__inv_1 _362_ (.A(net12),
    .Y(_039_));
 sky130_fd_sc_hd__nor3_1 _363_ (.A(net11),
    .B(net9),
    .C(net10),
    .Y(_177_));
 sky130_fd_sc_hd__inv_1 _364_ (.A(_177_),
    .Y(_178_));
 sky130_fd_sc_hd__nand2_1 _365_ (.A(_178_),
    .B(_173_),
    .Y(_179_));
 sky130_fd_sc_hd__xor2_1 _366_ (.A(_039_),
    .B(_179_),
    .X(_180_));
 sky130_fd_sc_hd__inv_1 _367_ (.A(_180_),
    .Y(_062_));
 sky130_fd_sc_hd__inv_1 _368_ (.A(_012_),
    .Y(_181_));
 sky130_fd_sc_hd__nand2_1 _369_ (.A(_173_),
    .B(_181_),
    .Y(_182_));
 sky130_fd_sc_hd__o21ai_0 _370_ (.A1(net10),
    .A2(_173_),
    .B1(_182_),
    .Y(_005_));
 sky130_fd_sc_hd__inv_1 _371_ (.A(_005_),
    .Y(_002_));
 sky130_fd_sc_hd__nor3_1 _372_ (.A(net11),
    .B(net12),
    .C(_174_),
    .Y(_183_));
 sky130_fd_sc_hd__inv_1 _373_ (.A(_183_),
    .Y(_184_));
 sky130_fd_sc_hd__nand2_1 _374_ (.A(_184_),
    .B(_173_),
    .Y(_185_));
 sky130_fd_sc_hd__xor2_1 _375_ (.A(net13),
    .B(_185_),
    .X(_017_));
 sky130_fd_sc_hd__o31ai_1 _376_ (.A1(net13),
    .A2(net12),
    .A3(_178_),
    .B1(_173_),
    .Y(_186_));
 sky130_fd_sc_hd__xor2_1 _377_ (.A(_029_),
    .B(_186_),
    .X(_187_));
 sky130_fd_sc_hd__inv_1 _378_ (.A(_187_),
    .Y(_013_));
 sky130_fd_sc_hd__o31ai_1 _379_ (.A1(net13),
    .A2(net14),
    .A3(_184_),
    .B1(_173_),
    .Y(_188_));
 sky130_fd_sc_hd__xor2_1 _380_ (.A(net15),
    .B(_188_),
    .X(_006_));
 sky130_fd_sc_hd__inv_1 _381_ (.A(net16),
    .Y(_058_));
 sky130_fd_sc_hd__inv_1 _382_ (.A(net20),
    .Y(_065_));
 sky130_fd_sc_hd__nand2_1 _383_ (.A(_034_),
    .B(_039_),
    .Y(_189_));
 sky130_fd_sc_hd__nand2_1 _384_ (.A(_029_),
    .B(_024_),
    .Y(_190_));
 sky130_fd_sc_hd__nor2_1 _385_ (.A(_189_),
    .B(_190_),
    .Y(_191_));
 sky130_fd_sc_hd__nand2_1 _386_ (.A(_191_),
    .B(_177_),
    .Y(_192_));
 sky130_fd_sc_hd__nand2_1 _387_ (.A(_192_),
    .B(_173_),
    .Y(_193_));
 sky130_fd_sc_hd__xor2_1 _388_ (.A(net8),
    .B(net16),
    .X(_194_));
 sky130_fd_sc_hd__nand2_1 _389_ (.A(_193_),
    .B(_194_),
    .Y(_195_));
 sky130_fd_sc_hd__inv_1 _390_ (.A(_194_),
    .Y(_196_));
 sky130_fd_sc_hd__nand3_1 _391_ (.A(_192_),
    .B(_196_),
    .C(_173_),
    .Y(_197_));
 sky130_fd_sc_hd__nand2_1 _392_ (.A(_195_),
    .B(_197_),
    .Y(_198_));
 sky130_fd_sc_hd__nand2_1 _393_ (.A(_008_),
    .B(_015_),
    .Y(_199_));
 sky130_fd_sc_hd__nor2_1 _394_ (.A(_130_),
    .B(_199_),
    .Y(_200_));
 sky130_fd_sc_hd__inv_1 _395_ (.A(_199_),
    .Y(_201_));
 sky130_fd_sc_hd__nand2_1 _396_ (.A(_134_),
    .B(_201_),
    .Y(_202_));
 sky130_fd_sc_hd__a21oi_1 _397_ (.A1(_008_),
    .A2(_014_),
    .B1(_007_),
    .Y(_203_));
 sky130_fd_sc_hd__nand2_1 _398_ (.A(_202_),
    .B(_203_),
    .Y(_204_));
 sky130_fd_sc_hd__a21oi_1 _399_ (.A1(_108_),
    .A2(_200_),
    .B1(_204_),
    .Y(_205_));
 sky130_fd_sc_hd__inv_1 _400_ (.A(_205_),
    .Y(_206_));
 sky130_fd_sc_hd__nand2_1 _401_ (.A(_198_),
    .B(_206_),
    .Y(_207_));
 sky130_fd_sc_hd__nand3_1 _402_ (.A(_195_),
    .B(_205_),
    .C(_197_),
    .Y(_208_));
 sky130_fd_sc_hd__nand3_1 _403_ (.A(_207_),
    .B(_208_),
    .C(_085_),
    .Y(_209_));
 sky130_fd_sc_hd__nor2_1 _404_ (.A(_061_),
    .B(_085_),
    .Y(_210_));
 sky130_fd_sc_hd__nor2_1 _405_ (.A(_087_),
    .B(_210_),
    .Y(_211_));
 sky130_fd_sc_hd__nand2_1 _406_ (.A(_209_),
    .B(_211_),
    .Y(_212_));
 sky130_fd_sc_hd__nor2_1 _407_ (.A(_059_),
    .B(_080_),
    .Y(_213_));
 sky130_fd_sc_hd__nor2_1 _408_ (.A(_075_),
    .B(_213_),
    .Y(_214_));
 sky130_fd_sc_hd__nand2_1 _409_ (.A(_212_),
    .B(_214_),
    .Y(_215_));
 sky130_fd_sc_hd__or2_2 _410_ (.A(_060_),
    .B(_076_),
    .X(_216_));
 sky130_fd_sc_hd__nand2_1 _411_ (.A(_215_),
    .B(_216_),
    .Y(_217_));
 sky130_fd_sc_hd__o211ai_1 _412_ (.A1(net7),
    .A2(_091_),
    .B1(_095_),
    .C1(_099_),
    .Y(_218_));
 sky130_fd_sc_hd__a21oi_1 _413_ (.A1(_217_),
    .A2(_091_),
    .B1(_218_),
    .Y(_073_));
 sky130_fd_sc_hd__o21ai_1 _414_ (.A1(_051_),
    .A2(_080_),
    .B1(_076_),
    .Y(_219_));
 sky130_fd_sc_hd__nor2_1 _415_ (.A(_053_),
    .B(_085_),
    .Y(_220_));
 sky130_fd_sc_hd__a211oi_2 _416_ (.A1(_085_),
    .A2(_022_),
    .B1(_087_),
    .C1(_220_),
    .Y(_221_));
 sky130_fd_sc_hd__o221ai_1 _417_ (.A1(_052_),
    .A2(_076_),
    .B1(_219_),
    .B2(_221_),
    .C1(_102_),
    .Y(_222_));
 sky130_fd_sc_hd__nand2_1 _418_ (.A(_094_),
    .B(net2),
    .Y(_223_));
 sky130_fd_sc_hd__a21oi_1 _419_ (.A1(_222_),
    .A2(_223_),
    .B1(_098_),
    .Y(_072_));
 sky130_fd_sc_hd__nand2_1 _420_ (.A(_104_),
    .B(_050_),
    .Y(_224_));
 sky130_fd_sc_hd__o21ai_1 _421_ (.A1(_004_),
    .A2(_104_),
    .B1(_224_),
    .Y(_225_));
 sky130_fd_sc_hd__nand2_1 _422_ (.A(_225_),
    .B(_080_),
    .Y(_226_));
 sky130_fd_sc_hd__o211ai_2 _423_ (.A1(_048_),
    .A2(_080_),
    .B1(_076_),
    .C1(_226_),
    .Y(_227_));
 sky130_fd_sc_hd__o211ai_1 _424_ (.A1(_049_),
    .A2(_076_),
    .B1(_091_),
    .C1(_227_),
    .Y(_228_));
 sky130_fd_sc_hd__nand2_1 _425_ (.A(_090_),
    .B(net1),
    .Y(_229_));
 sky130_fd_sc_hd__o21ai_0 _426_ (.A1(net3),
    .A2(_095_),
    .B1(_099_),
    .Y(_230_));
 sky130_fd_sc_hd__a31oi_1 _427_ (.A1(_228_),
    .A2(_095_),
    .A3(_229_),
    .B1(_230_),
    .Y(_071_));
 sky130_fd_sc_hd__fa_1 _428_ (.A(_000_),
    .B(_001_),
    .CIN(_002_),
    .COUT(_003_),
    .SUM(_004_));
 sky130_fd_sc_hd__ha_1 _429_ (.A(net7),
    .B(_006_),
    .COUT(_007_),
    .SUM(_008_));
 sky130_fd_sc_hd__ha_1 _430_ (.A(_009_),
    .B(_010_),
    .COUT(_011_),
    .SUM(_012_));
 sky130_fd_sc_hd__ha_1 _431_ (.A(net6),
    .B(_013_),
    .COUT(_014_),
    .SUM(_015_));
 sky130_fd_sc_hd__ha_1 _432_ (.A(net5),
    .B(_017_),
    .COUT(_018_),
    .SUM(_019_));
 sky130_fd_sc_hd__ha_1 _433_ (.A(net2),
    .B(_005_),
    .COUT(_020_),
    .SUM(_016_));
 sky130_fd_sc_hd__ha_1 _434_ (.A(_021_),
    .B(net9),
    .COUT(_001_),
    .SUM(_022_));
 sky130_fd_sc_hd__ha_1 _435_ (.A(_023_),
    .B(_024_),
    .COUT(_025_),
    .SUM(_026_));
 sky130_fd_sc_hd__ha_1 _436_ (.A(net7),
    .B(net15),
    .COUT(_027_),
    .SUM(_231_));
 sky130_fd_sc_hd__ha_1 _437_ (.A(_028_),
    .B(_029_),
    .COUT(_030_),
    .SUM(_031_));
 sky130_fd_sc_hd__ha_1 _438_ (.A(net6),
    .B(net14),
    .COUT(_032_),
    .SUM(_232_));
 sky130_fd_sc_hd__ha_1 _439_ (.A(_033_),
    .B(_034_),
    .COUT(_035_),
    .SUM(_036_));
 sky130_fd_sc_hd__ha_1 _440_ (.A(net5),
    .B(net13),
    .COUT(_037_),
    .SUM(_233_));
 sky130_fd_sc_hd__ha_1 _441_ (.A(_038_),
    .B(_039_),
    .COUT(_040_),
    .SUM(_041_));
 sky130_fd_sc_hd__ha_1 _442_ (.A(net4),
    .B(net12),
    .COUT(_042_),
    .SUM(_234_));
 sky130_fd_sc_hd__ha_1 _443_ (.A(_043_),
    .B(_044_),
    .COUT(_045_),
    .SUM(_046_));
 sky130_fd_sc_hd__ha_1 _444_ (.A(net3),
    .B(net11),
    .COUT(_047_),
    .SUM(_235_));
 sky130_fd_sc_hd__ha_1 _445_ (.A(_000_),
    .B(_009_),
    .COUT(_048_),
    .SUM(_049_));
 sky130_fd_sc_hd__ha_1 _446_ (.A(net2),
    .B(net10),
    .COUT(_050_),
    .SUM(_236_));
 sky130_fd_sc_hd__ha_1 _447_ (.A(_021_),
    .B(_010_),
    .COUT(_051_),
    .SUM(_052_));
 sky130_fd_sc_hd__ha_1 _448_ (.A(net1),
    .B(net9),
    .COUT(_053_),
    .SUM(_237_));
 sky130_fd_sc_hd__ha_1 _449_ (.A(net3),
    .B(_054_),
    .COUT(_055_),
    .SUM(_056_));
 sky130_fd_sc_hd__ha_1 _450_ (.A(_057_),
    .B(_058_),
    .COUT(_059_),
    .SUM(_060_));
 sky130_fd_sc_hd__ha_1 _451_ (.A(net8),
    .B(net16),
    .COUT(_061_),
    .SUM(_238_));
 sky130_fd_sc_hd__ha_1 _452_ (.A(net4),
    .B(_062_),
    .COUT(_063_),
    .SUM(_064_));
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
 sky130_fd_sc_hd__clkdlybuf4s50_1 input17 (.A(op[0]),
    .X(net17));
 sky130_fd_sc_hd__clkdlybuf4s50_1 input18 (.A(op[1]),
    .X(net18));
 sky130_fd_sc_hd__clkdlybuf4s50_1 input19 (.A(op[2]),
    .X(net19));
 sky130_fd_sc_hd__clkdlybuf4s50_1 input2 (.A(a[1]),
    .X(net2));
 sky130_fd_sc_hd__clkdlybuf4s50_1 input20 (.A(reset),
    .X(net20));
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
 sky130_fd_sc_hd__clkdlybuf4s50_1 output21 (.A(net21),
    .X(y[0]));
 sky130_fd_sc_hd__clkdlybuf4s50_1 output22 (.A(net22),
    .X(y[1]));
 sky130_fd_sc_hd__clkdlybuf4s50_1 output23 (.A(net23),
    .X(y[2]));
 sky130_fd_sc_hd__clkdlybuf4s50_1 output24 (.A(net24),
    .X(y[3]));
 sky130_fd_sc_hd__clkdlybuf4s50_1 output25 (.A(net25),
    .X(y[4]));
 sky130_fd_sc_hd__clkdlybuf4s50_1 output26 (.A(net26),
    .X(y[5]));
 sky130_fd_sc_hd__clkdlybuf4s50_1 output27 (.A(net27),
    .X(y[6]));
 sky130_fd_sc_hd__clkdlybuf4s50_1 output28 (.A(net28),
    .X(y[7]));
 sky130_fd_sc_hd__dfrtp_1 \y[0]$_DFFE_PP0P_  (.D(_072_),
    .Q(net21),
    .RESET_B(_065_),
    .CLK(clknet_1_0__leaf_clk));
 sky130_fd_sc_hd__dfrtp_1 \y[1]$_DFFE_PP0P_  (.D(_071_),
    .Q(net22),
    .RESET_B(_065_),
    .CLK(clknet_1_0__leaf_clk));
 sky130_fd_sc_hd__dfrtp_1 \y[2]$_DFFE_PP0P_  (.D(_070_),
    .Q(net23),
    .RESET_B(_065_),
    .CLK(clknet_1_0__leaf_clk));
 sky130_fd_sc_hd__dfrtp_1 \y[3]$_DFFE_PP0P_  (.D(_069_),
    .Q(net24),
    .RESET_B(_065_),
    .CLK(clknet_1_0__leaf_clk));
 sky130_fd_sc_hd__dfrtp_1 \y[4]$_DFFE_PP0P_  (.D(_068_),
    .Q(net25),
    .RESET_B(_065_),
    .CLK(clknet_1_1__leaf_clk));
 sky130_fd_sc_hd__dfrtp_1 \y[5]$_DFFE_PP0P_  (.D(_067_),
    .Q(net26),
    .RESET_B(_065_),
    .CLK(clknet_1_1__leaf_clk));
 sky130_fd_sc_hd__dfrtp_1 \y[6]$_DFFE_PP0P_  (.D(_066_),
    .Q(net27),
    .RESET_B(_065_),
    .CLK(clknet_1_1__leaf_clk));
 sky130_fd_sc_hd__dfrtp_1 \y[7]$_DFFE_PP0P_  (.D(_073_),
    .Q(net28),
    .RESET_B(_065_),
    .CLK(clknet_1_1__leaf_clk));
endmodule
