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

`ifndef __COUNTER
`define __COUNTER

/*
This module implements a counter. This counter can run in an overflow mode or it is limited. This means that it counts from -amplidude to +amplidude.
*/
module counter #(
    parameter N_FRAC = 7 // fractional part of the Q notation (Q0.{N_FRAC}) that is used
) (
    // inputs
    input clk_i, // clock of the system
    input rst_i, // reset (active low) of the system
    input signed [N_FRAC:0] amplitude_i, // amplidude for the limited mode
    input signed [N_FRAC:0] addend_i, // value that is added per requested value
    input overflow_mode_i, // defines the mode of the counter (1 overflow mode and 0 limited mode)				
    input get_next_data_strobe_i, // strobe to request the next value from the counter					
    
    // outputs
    output wire signed [N_FRAC:0] data_o, // current value of the counter						
    output wire data_out_valid_strobe_o // strobe to identifiy a new value on the output 
);
     // register variables next_ defines the input for the register and without next_ the actual value is defined
    reg signed [N_FRAC:0] counter_value, next_counter_value;
    reg data_out_valid_strobe, next_data_out_valid_strobe;

    // registers
    always @(posedge clk_i) begin
        if (rst_i == 1'b0) begin
            counter_value <= 0;
            data_out_valid_strobe <= 0;
        end else begin
            counter_value <= next_counter_value;
            data_out_valid_strobe <= next_data_out_valid_strobe;
        end
    end 

    // combinational logic
    always @* begin
        // default assignment
        next_data_out_valid_strobe = 0;
        next_counter_value = counter_value;
        
        if (get_next_data_strobe_i == 1'b1) begin
            // new value is reuested
            next_data_out_valid_strobe = 1;
            if ((overflow_mode_i == 1'b1) || (counter_value <= amplitude_i)) begin
                // in the overflow mode the counter will overflow
                // in the limited mode the counter will only add if the current value is smaller than the given amplidude
                next_counter_value = counter_value + addend_i;
            end else begin
                // negate the current value for the limited mode
                next_counter_value = -counter_value;
            end
        end
    end

    // assign the register outputs to the outputs of the module
    assign data_o = counter_value;
    assign data_out_valid_strobe_o = data_out_valid_strobe;

endmodule

`endif
`default_nettype wire
