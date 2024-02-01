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
`ifndef __SIN_GENERATOR
`define __SIN_GENERATOR

`include "cordic_convergence.v"
`include "cordic_iterative.v"

/*
This module generate a sinus with the help of a cordic algorithm. The sin can have a specified amplidude and frequency. The frequency is controlled by the given phase per requested value.  
*/
module sin_generator #(
    parameter N_FRAC = 7 // fractional part of the Q notation (Q0.{N_FRAC}) that is used
) (
    // inputs
    input clk_i, // clock of the system
    input rst_i, // reset (active low) of the system
    input signed [N_FRAC:0] phase_i, // phase value that is added per interaction
    input signed [N_FRAC:0] amplitude_i, // ampludude value of the sin						
    input get_next_data_strobe_i, // strobe to push the next output value

    // outputs 						
    output wire signed [N_FRAC:0] data_o, // calaculated sinus					
    output wire data_out_valid_strobe_o	 // strobe that identifies that the unit finished with the calculation
);    
    // register variables next_defines the input of the register and without next_ the actual value is defined
    reg signed [N_FRAC:0] z_phase, next_z_phase;
    reg phase_increment_done_strobe, next_phase_increment_done_strobe;

    // wires for combinational logic
    wire signed [N_FRAC:0] y_con_out, x_con_out, z_con_out;
    wire data_con_out_valid_strobe;
    wire signed [N_FRAC:0] y_cordic_out;
    /* verilator lint_off UNUSEDSIGNAL */
    wire signed [N_FRAC:0] x_cordic_out, z_cordic_out;
    /* verilator lint_on UNUSEDSIGNAL */
    wire data_cordic_out_valid_strobe;

    // to get a sin or cos we set the y input of the cordic to zero
    wire signed [N_FRAC:0] y_const;
    assign y_const = 0;

    // registers
    always @(posedge clk_i) begin
        if (rst_i == 1'b0) begin
            z_phase <= 0;
            phase_increment_done_strobe <= 0;
        end else begin
            z_phase <= next_z_phase;
            phase_increment_done_strobe <= next_phase_increment_done_strobe;
        end
    end

    // combinational logic for adding the phase_i to the old phase
    always @* begin
        next_phase_increment_done_strobe = 0;
        next_z_phase = z_phase;
        
        if (get_next_data_strobe_i == 1'b1) begin
            next_phase_increment_done_strobe = 1;
            next_z_phase = z_phase + phase_i;
        end
    end

    // checks if the phase is between +90° and -90°. if not it performs a direct rotation
    cordic_convergence cordic_convergence_inst
    (.clk_i(clk_i),
     .rst_i(rst_i),
     .x_i(amplitude_i),
     .y_i(y_const),
     .z_i(z_phase),
     .data_in_valid_strobe_i(phase_increment_done_strobe),
     .x_o(x_con_out),
     .y_o(y_con_out),
     .z_o(z_con_out),
     .data_out_valid_strobe_o(data_con_out_valid_strobe)
     );

    // calculate the sin and cos values for the given phase
    cordic_iterative cordic_iterative_inst
    (.clk_i(clk_i),
     .rst_i(rst_i),
     .x_i(x_con_out),
     .y_i(y_con_out),
     .z_i(z_con_out),
     .data_in_valid_strobe_i(data_con_out_valid_strobe),
     .x_o(x_cordic_out),
     .y_o(y_cordic_out),
     .z_o(z_cordic_out),
     .data_out_valid_strobe_o(data_cordic_out_valid_strobe)
     );

    // assign the register outputs to the outputs of the module
    assign data_o = y_cordic_out; // only the sin is needed therefore we use the y output of the cordic
    assign data_out_valid_strobe_o = data_cordic_out_valid_strobe;
    
endmodule

`endif
`default_nettype wire
