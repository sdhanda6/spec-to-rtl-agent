module fp16_multiplier (clk,
    reset,
    a,
    b,
    result);
 input clk;
 input reset;
 input [15:0] a;
 input [15:0] b;
 output [15:0] result;


 sky130_fd_sc_hd__conb_1 _02__1 (.LO(result[0]));
 sky130_fd_sc_hd__conb_1 _03__2 (.LO(result[1]));
 sky130_fd_sc_hd__conb_1 _04__3 (.LO(result[2]));
 sky130_fd_sc_hd__conb_1 _05__4 (.LO(result[3]));
 sky130_fd_sc_hd__conb_1 _06__5 (.LO(result[4]));
 sky130_fd_sc_hd__conb_1 _07__6 (.LO(result[5]));
 sky130_fd_sc_hd__conb_1 _08__7 (.LO(result[6]));
 sky130_fd_sc_hd__conb_1 _09__8 (.LO(result[7]));
 sky130_fd_sc_hd__conb_1 _10__9 (.LO(result[8]));
 sky130_fd_sc_hd__conb_1 _11__10 (.LO(result[9]));
 sky130_fd_sc_hd__conb_1 _12__11 (.LO(result[10]));
 sky130_fd_sc_hd__conb_1 _13__12 (.LO(result[11]));
 sky130_fd_sc_hd__conb_1 _14__13 (.LO(result[12]));
 sky130_fd_sc_hd__conb_1 _15__14 (.LO(result[13]));
 sky130_fd_sc_hd__conb_1 _16__15 (.LO(result[14]));
 sky130_fd_sc_hd__conb_1 _17__16 (.LO(result[15]));
endmodule
