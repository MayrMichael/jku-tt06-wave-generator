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

`ifndef __WAVE_GENERATOR
`define __WAVE_GENERATOR

`include "sin_generator.v"
`include "top_triangle_generator.v"
`include "strobe_generator.v"

/*
This module is the top module for all signal generation modules. 
*/
module wave_generator #(
    parameter N_FRAC = 7 // fractional part of the Q notation (Q0.{N_FRAC}) that is used
) (
    // inputs
    input clk_i, // clock of the system
    input rst_i, // reset (active low) of the system
    input enable_i, // if high new samples are generated
    input [1:0] waveform_i, // defines the wanted output signal 
    input set_phase_strobe_i, // strobe to set data_i as the the new phase value
    input set_amplitude_strobe_i, // storbe to set data_i as the new amplidude value
    input signed [N_FRAC:0] data_i, // defines the phase value or the amplidude value
    
    // outputs
    output wire signed [N_FRAC:0] data_o, // output sample of the requestet signal
    output wire data_valid_strobe_o // strobe that indicates a new output sample
);
    // different signals that can be generated
    localparam SINUS = 2'b00;
    localparam SQUARE_PULSE = 2'b01;
    localparam SAWTOOTH = 2'b10;
    localparam TRIANGLE = 2'b11;

    // register variables for the phase
    reg signed [N_FRAC:0] phase;
    wire signed [N_FRAC:0] next_phase;

    // register variables for the amplidude
    reg signed [N_FRAC:0] amplitude;
    wire signed [N_FRAC:0] next_amplitude;

    // register values for the outputs of the module
    reg data_valid_strobe, next_data_valid_strobe;
    reg signed [N_FRAC:0] data, next_data;

    // wires to connect the different modules together 
    wire strobe;
    wire overflow_mode;
    wire signed [N_FRAC:0] data_sin, data_triangle, data_sawtooth, data_square_puls;
    wire data_sin_out_valid_strobe, data_triangle_out_valid_strobe, data_sawtooth_out_valid_strobe,  data_square_puls_out_valid_strobe;

    // the interal counter of the top_triangle_generator should go in overflow_mode only when the square pulse is needed
    assign overflow_mode = waveform_i == SQUARE_PULSE ? 1'b1 : 1'b0;

    // generate a strobe every 40 clk cycles
    strobe_generator strobe_generator_inst
    (.clk_i(clk_i),
     .rst_i(rst_i),
     .enable_i(enable_i),
     .strobe_o(strobe)
    );

    // generate the sinus samples
    sin_generator sin_generator_inst
    (.clk_i(clk_i),
     .rst_i(rst_i),
     .phase_i(phase),
     .amplitude_i(amplitude),
     .get_next_data_strobe_i(strobe),
     .data_o(data_sin),
     .data_out_valid_strobe_o(data_sin_out_valid_strobe)
    );

    // generate the sawtooth, triangle and square pulse samples
    top_triangle_generator top_triangle_generator_inst
    (.clk_i(clk_i),
     .rst_i(rst_i),
     .phase_i(phase),
     .amplitude_i(amplitude),
     .overflow_mode_i(overflow_mode),					
     .get_next_data_strobe_i(strobe), 						
     .data_sawtooth_o(data_sawtooth),						
     .data_sawtooth_out_valid_strobe_o(data_sawtooth_out_valid_strobe),
     .data_triangle_o(data_triangle),						
     .data_triangle_out_valid_strobe_o(data_triangle_out_valid_strobe),
     .data_square_puls_o(data_square_puls),
     .data_square_puls_out_valid_strobe_o(data_square_puls_out_valid_strobe)
    );

    // registers
    always @(posedge clk_i) begin
        if (rst_i == 1'b0) begin
            data <= 0;
            data_valid_strobe <= 0;
            phase <= 0;
            amplitude <= 0;
        end else begin
            phase <= next_phase;
            amplitude <= next_amplitude;
            data <= next_data;
            data_valid_strobe <= next_data_valid_strobe;
        end
    end

    // combinational logic
    always @* begin
        // default assignments
        next_data_valid_strobe = data_valid_strobe;
        next_data = data;

        // mux to get the right output signal to the out flipflop
        case (waveform_i)
            SINUS: begin
                next_data_valid_strobe = data_sin_out_valid_strobe;
                if (data_sin_out_valid_strobe == 1'b1) 
                    next_data = data_sin;
            end 
            SAWTOOTH: begin
                next_data_valid_strobe = data_sawtooth_out_valid_strobe;
                if (data_sawtooth_out_valid_strobe == 1'b1) 
                    next_data = data_sawtooth;
            end
            TRIANGLE: begin
                next_data_valid_strobe = data_triangle_out_valid_strobe;
                if (data_triangle_out_valid_strobe == 1'b1) 
                    next_data = data_triangle;
            end
            SQUARE_PULSE: begin
                next_data_valid_strobe = data_square_puls_out_valid_strobe;
                if (data_square_puls_out_valid_strobe == 1'b1) 
                    next_data = data_square_puls;
            end
        endcase
    end

    // set the new phase
    assign next_phase = (set_phase_strobe_i == 1'b1) ? data_i : phase;
    
    // set the new amplidude
    assign next_amplitude = (set_amplitude_strobe_i == 1'b1) ? data_i : amplitude; 

    // assign the register outputs to the outputs of the module
    assign data_o = data;
    assign data_valid_strobe_o = data_valid_strobe;

endmodule

`endif
`default_nettype wire
