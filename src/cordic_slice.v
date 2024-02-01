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

`ifndef __CORDIC_SLICE
`define __CORDIC_SLICE

/*
This module implements a single cordic iteration. The slice support only rotation mode in the circular coordinate system.
*/
module cordic_slice #(
    parameter BW_SHIFT_VALUE = 4, // Bitwidth of the shift bitvector
    parameter N_FRAC = 15 // fractional part of the Q notation (Q0.{N_FRAC})
) (
    // inputs
    input clk_i, // clock of the system                                     
    input rst_i, // reset (active low) of the system
    input signed [N_FRAC:0] current_rotation_angle_i, // rotation angle that is added or subtracted then from z_i	
    input [BW_SHIFT_VALUE-1:0] shift_value_i, // exponent to the base of 2			
    input signed [N_FRAC:0] x_i, // input for x					
    input signed [N_FRAC:0] y_i, // input for y						
    input signed [N_FRAC:0] z_i, // input for z
    
    // outputs defined as registers					
    output reg signed [N_FRAC:0] x_o, // output for x						
    output reg signed [N_FRAC:0] y_o, // output for y						
    output reg signed [N_FRAC:0] z_o  // output for z						
);
    reg signed [N_FRAC:0] next_x; // input for the register x_o
    reg signed [N_FRAC:0] next_y; // input for the register y_o
    reg signed [N_FRAC:0] next_z; // input for the register z_o

    // register logic
    always @(posedge clk_i) begin
        if (rst_i == 1'b0) begin
            x_o <= 0;
            y_o <= 0;
            z_o <= 0;
        end else begin
            x_o <= next_x;
            y_o <= next_y;
            z_o <= next_z;            
        end
    end

    // combinational logic
    always @* begin
        next_x = x_i;
	    next_y = y_i;
	    next_z = z_i;

        // The aim is for the resulting z_o to be closer to 0 than z_i.
        // Therefore we check if z_i is greater or smaller than zero.
        if (z_i < 0) begin
            // single iteration in the case z_i is smaller than 0
            next_x = x_i + (y_i >>> shift_value_i);
            next_y = y_i - (x_i >>> shift_value_i);
		    next_z = z_i + current_rotation_angle_i;
        end else begin
            // single iteration in the case z_i is greter or equal  to 0
            next_x = x_i - (y_i >>> shift_value_i);
            next_y = y_i + (x_i >>> shift_value_i);
		    next_z = z_i - current_rotation_angle_i;
        end
    end

endmodule

`endif
`default_nettype wire
