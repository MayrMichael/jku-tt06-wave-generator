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

`ifndef __TRIANGLE_GENERATOR
`define __TRIANGLE_GENERATOR

/*
This module transfers a counter value that is a sawtooth to a triangle function.
*/
module triangle_generator #(
    parameter N_FRAC = 7 // fractional part of the Q notation (Q0.{N_FRAC}) that is used
) (
    // inputs
    input clk_i, // clock of the system
    input rst_i, // reset (active low) of the system
    input signed [N_FRAC:0] counter_value_i, // value of the counter to transform to a triangle wave			
    input next_counter_value_strobe_i, // strobe that identifies a new value from the counter						
    
    // outputs
    output wire signed [N_FRAC:0] data_o, // output of the triangle wave						
    output wire data_out_valid_strobe_o // strobe that indenticate a new value on the output
);
    // register variables next_ defines the input for the register and without next_ the actual value is defined
    reg signed [N_FRAC:0] data, next_data;
    reg data_out_valid_strobe, next_data_out_valid_strobe;
    reg reverse, next_reverse;
    reg old_signed_bit, next_old_signed_bit;
    reg counter, next_counter;
    reg state, next_state;

    // states for the state machine
    localparam IDLE_STATE = 1'b0;
    localparam CALCULATION_STATE = 1'b1;

    // registers
    always @(posedge clk_i) begin
        if (rst_i == 1'b0) begin
            state <= IDLE_STATE;
            old_signed_bit <= 0;
            counter <= 0;
            reverse <= 0;
            data <= 0;
            data_out_valid_strobe <= 0;
        end else begin
            state <= next_state;
            old_signed_bit <= next_old_signed_bit;
            counter <= next_counter;
            reverse <= next_reverse;
            data <= next_data;
            data_out_valid_strobe <= next_data_out_valid_strobe;
        end
    end

    // combinational logic with a state machine
    always @* begin
        // default assignments
        next_state = state;
        next_old_signed_bit = old_signed_bit;
        next_counter = counter;
        next_reverse = reverse;
        next_data = data;
        next_data_out_valid_strobe = 0;

        case (state)
            IDLE_STATE: begin
                // wait for a new counter value
                if (next_counter_value_strobe_i == 1'b1) begin
                    next_state = CALCULATION_STATE;
                    next_old_signed_bit = counter_value_i[N_FRAC]; // store current signed bit for next iteration
                    if (old_signed_bit != counter_value_i[N_FRAC]) begin
                        // if the current sign bit divers from the old sign bit a overflow of the counter happend.
                        if (counter == 1'b0) begin
                            // every second sawtooth has to be reversed to generate a triangle wave
                            next_counter = 1;
                            next_reverse = ~reverse;
                        end else begin
                            next_counter = 0;
                        end
                    end
                end
            end 
            CALCULATION_STATE: begin
                // transform sawtooth to triangle wave
                next_data_out_valid_strobe = 1;
                next_state = IDLE_STATE;
                if (reverse == 1'b1) begin
                    // reverse the values of the sawtooth
                    next_data = -counter_value_i;
                end else begin
                    // keep tha values of the sawtooth
                    next_data = counter_value_i;
                end
            end
            default:
                next_state = IDLE_STATE;
        endcase
    end

    // assign the register outputs to the outputs of the module
    assign data_o = data;
    assign data_out_valid_strobe_o = data_out_valid_strobe;

endmodule

`endif
`default_nettype wire
