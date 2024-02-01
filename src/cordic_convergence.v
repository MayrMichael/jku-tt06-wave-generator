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

`ifndef __CORDIC_CONVERGENCE
`define __CORDIC_CONVERGENCE

/*
This module check the convergence criteria. This is needed because the operating range (region of convergence) of the 
CORDIC algorithm is at about -100°…100°.
*/
module cordic_convergence #(
    parameter N_FRAC = 7 // fractional part of the Q notation (Q0.{N_FRAC}) that is used
) (
    // inputs
    input clk_i, // clock of the system
    input rst_i, // reset (active low) of the system
    input signed [N_FRAC:0] x_i, // input for x							
    input signed [N_FRAC:0] y_i, // input for y						
    input signed [N_FRAC:0] z_i, // input for z
    input data_in_valid_strobe_i, // strobe that is true if the values x_i, y_i and z_i are ready for the algorithm

    // outputs
    output reg signed [N_FRAC:0] x_o, // output for x						
    output reg signed [N_FRAC:0] y_o, // output for y							
    output reg signed [N_FRAC:0] z_o, // output for z
    output reg data_out_valid_strobe_o // strobe that is true if the calaulation is performed and the values are ready to deliver.
);
    // the boarders of the region on convergence ( +90° and -90°) 
    localparam signed HALF = 8'sb01000000;
    localparam signed MINUS_HALF = 8'sb11000000;

    // register variables for the input of the register
    reg signed [N_FRAC:0] next_x;
    reg signed [N_FRAC:0] next_y;
    reg signed [N_FRAC:0] next_z;

    // registers
    always @(posedge clk_i) begin
        if (rst_i == 1'b0) begin
            x_o <= 0;
            y_o <= 0;
            z_o <= 0;
            data_out_valid_strobe_o <= 0;
        end else begin
            x_o <= next_x;
            y_o <= next_y;
            z_o <= next_z;
            data_out_valid_strobe_o <= data_in_valid_strobe_i;          
        end
    end

    // combinational logic
    always @* begin
        // default assignments
        next_x = x_i;
        next_y = y_i;
        next_z = z_i;

        if (z_i > HALF) begin
            // is rotation greater than 0.5 pi? yes: rotate by hand 90° and subtract from z
            next_x = -y_i;
            next_y = x_i;
            next_z = MINUS_HALF + z_i;
        end else if (z_i < MINUS_HALF) begin
            // is rotation smaller than -0.5 pi? yes: rotate by hand -90° and add to z
            next_x = y_i;
            next_y = -x_i;
            next_z = HALF + z_i;            
        end
    end
    
endmodule

`endif
`default_nettype wire
