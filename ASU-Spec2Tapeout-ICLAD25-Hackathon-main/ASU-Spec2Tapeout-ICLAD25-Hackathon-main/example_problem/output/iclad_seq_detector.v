module seq_detector_0011(
    input clk,
    input reset,
    input data_in,
    output reg detected
);

// State encoding using parameters
parameter IDLE  = 3'b000,
          S0    = 3'b001,
          S00   = 3'b010,
          S001  = 3'b011,
          S0011 = 3'b100;

reg [2:0] current_state, next_state;

// State transition
always @(posedge clk or posedge reset) begin
    if(reset) 
        current_state <= IDLE;
    else
        current_state <= next_state;
end

// Next state logic
always @(*) begin
    case(current_state)
        IDLE: next_state = (data_in == 1'b0) ? S0 : IDLE;
        S0:   next_state = (data_in == 1'b0) ? S00 : IDLE;
        S00:  next_state = (data_in == 1'b1) ? S001 : S00;
        S001: next_state = (data_in == 1'b1) ? S0011 : S0;
        S0011:next_state = (data_in == 1'b0) ? S0 : IDLE;
        default: next_state = IDLE;
    endcase
end

// Output logic
always @(posedge clk or posedge reset) begin
    if(reset)
        detected <= 1'b0;
    else
        detected <= (next_state == S0011);
end

endmodule
