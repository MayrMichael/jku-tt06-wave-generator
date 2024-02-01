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

`ifndef __TOP_TRIANGLE_GENERATOR
`define __TOP_TRIANGLE_GENERATOR

`include "counter.v"
`include "triangle_generator.v"
`include "square_puls_generator.v"

/*
This module generates a sawtooth wave, a triangle wave and a square puls wave from given parameters
*/
module top_triangle_generator #(
    parameter N_FRAC = 7 // fractional part of the Q notation (Q0.{N_FRAC}) that is used
) (
    // inputs
    input clk_i, // clock of the system
    input rst_i, // reset (active low) of the system
    input signed [N_FRAC:0] phase_i, // value that is accumulated per iteration
    input signed [N_FRAC:0] amplitude_i, // amplidude for sawtooth wave and triangle wave and for the square puls it is used as threshold.
    input overflow_mode_i, // if the square puls values are needed the overflow mode has to be 1. Then the other waves have also the max possible amplidude.		
    input get_next_data_strobe_i, // strobe to request the next value						
    
    // outputs
    output wire signed [N_FRAC:0] data_sawtooth_o, // sawtooth wave						
    output wire data_sawtooth_out_valid_strobe_o, // strobe that indenticate a new sawtooth wave value
    output wire signed [N_FRAC:0] data_triangle_o, // triangle wave						
    output wire data_triangle_out_valid_strobe_o, // strobe that indenticate a new triangle wave value
    output wire signed [N_FRAC:0] data_square_puls_o, // square puls						
    output wire data_square_puls_out_valid_strobe_o	// strobe that indenticate a new square puls wave value
);
    // wires for the connection between the counter and the other units.
    wire signed [N_FRAC:0] counter_value;
    wire counter_value_valid_strobe;

    // generates a sawtooth wave controlled by the phase and the provided mode
    counter counter_inst
    (.clk_i(clk_i),
     .rst_i(rst_i),
     .amplitude_i(amplitude_i),
     .addend_i(phase_i),
     .overflow_mode_i(overflow_mode_i),			
     .get_next_data_strobe_i(get_next_data_strobe_i), 						
     .data_o(counter_value),						
     .data_out_valid_strobe_o(counter_value_valid_strobe)
    );

    // assign the counter values directly to the output values
    assign data_sawtooth_out_valid_strobe_o = counter_value_valid_strobe;
    assign data_sawtooth_o = counter_value;

    // transform the sawtooth values to triangle values
    triangle_generator triangle_generator_inst
    (.clk_i(clk_i),
     .rst_i(rst_i),
     .counter_value_i(counter_value),			
     .next_counter_value_strobe_i(counter_value_valid_strobe), 						
     .data_o(data_triangle_o),						
     .data_out_valid_strobe_o(data_triangle_out_valid_strobe_o)
    );

    // transform the sawtooth values to square puls values
    square_puls_generator square_puls_generator_inst
    (.clk_i(clk_i),
     .rst_i(rst_i),
     .threshold_i(amplitude_i),
     .counter_value_i(counter_value),		
     .counter_value_valid_strobe_i(counter_value_valid_strobe), 						
     .data_o(data_square_puls_o),						
     .data_out_valid_strobe_o(data_square_puls_out_valid_strobe_o)
    );

endmodule

`endif
`default_nettype wire
