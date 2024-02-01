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

`ifndef __STROBE_GENERATOR
`define __STROBE_GENERATOR

/*
This module generates a strobe after a defined number of clks
*/
module strobe_generator #(
    parameter CLKS_PER_STROBE = 40 // defines the number of clks between two strobes
) (
    // inputs
    input clk_i, // clock of the system
    input rst_i, // reset (active low) of the system
    input enable_i, // enables the strobe generation						
    
    // output
    output wire strobe_o // output for the strobes
);
    // register variables next_ defines the input for the register and without next_ the actual value is defined
    reg [$clog2(CLKS_PER_STROBE*2)-1:0] counter, next_counter;
    reg strobe, next_strobe;

    // registers
    always @(posedge clk_i) begin
        if (rst_i == 1'b0) begin
            counter <= 0;
            strobe <= 0;
        end else begin
            counter <= next_counter;
            strobe <= next_strobe;
        end
    end

    // combinational logic
    always @* begin
        // default assignment
        next_counter = counter;
        next_strobe = 1'b0;
        
        if (enable_i == 1'b1) begin
            // the enable must be true to run the internal counter
            if (counter == CLKS_PER_STROBE-1) begin
                // strobe is send out
                next_counter = 0;
                next_strobe = 1'b1;
            end else begin
                next_counter = counter + 1;
            end
        end
    end

     // assign the register output to the output of the module
    assign strobe_o = strobe;

endmodule

`endif
`default_nettype wire
