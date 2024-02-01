// Copyright 2024 Michael Mayr
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
// http://www.apache.org/licenses/LICENSE−2.0
//
// Unless required by applicable law or agreed to in writing, software
/// distributed under the License is distributed on an "AS IS" BASIS,
/// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
/// See the License for the specific language governing permissions and
/// limitations under the License.

`default_nettype none

`ifndef __SQUARE_PULS_GENERATOR
`define __SQUARE_PULS_GENERATOR

/*
This module generates from a sawtooth a square puls wave. Therfore a threshold is given to set the output to -1+LSB or 1-LSB.
*/
module square_puls_generator #(
    parameter N_FRAC = 7 // fractional part of the Q notation (Q0.{N_FRAC}) that is used
) (
    // inputs
    input clk_i, // clock of the system
    input rst_i, // reset (active low) of the system
    input signed [N_FRAC:0] threshold_i, // threshold for the decision if the output is -1+LSB or 1-LSB
    input signed [N_FRAC:0] counter_value_i, // current counter value 		
    input counter_value_valid_strobe_i, // strobe that identifies a new value from the counter						
    
    // outputs
    output wire signed [N_FRAC:0] data_o, // output of the square puls wave						
    output wire data_out_valid_strobe_o // strobe that indenticate a new value on the output
);
    // const values to define 1-LSB an and -1+LSB
    localparam ONE = 8'b0111_1111;
    localparam MINUS_ONE = 8'b1000_0001; 

    // register variables next_ defines the input for the register and without next_ the actual value is defined
    reg signed [N_FRAC:0] data, next_data;
    reg data_out_valid_strobe, next_data_out_valid_strobe;

    // registers
    always @(posedge clk_i) begin
        if (rst_i == 1'b0) begin
            data <= 0;
            data_out_valid_strobe <= 0;
        end else begin
            data <= next_data;
            data_out_valid_strobe <= next_data_out_valid_strobe;
        end
    end 

    // combinational logic
    always @* begin
        next_data_out_valid_strobe = 0;
        next_data = data;
        
        if (counter_value_valid_strobe_i == 1'b1) begin
            // a new counter value arrived
            next_data_out_valid_strobe = 1;
            if (counter_value_i >= threshold_i) begin
                next_data = ONE;
            end else begin
                next_data = MINUS_ONE;
            end
        end
    end

    // assign the register outputs to the outputs of the module
    assign data_o = data;
    assign data_out_valid_strobe_o = data_out_valid_strobe;

endmodule

`endif
`default_nettype wire
