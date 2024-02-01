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

`ifndef __CORDIC_ITERATIVE
`define __CORDIC_ITERATIVE

`include "cordic_slice.v"

/*
This module implements a iterative cordic solution that can only perform rotation in the circular coordinate system. 
That uses the cordic slice module to create the desired values.
*/
module cordic_iterative #(
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
    output wire signed [N_FRAC:0] x_o, // output for x 					
    output wire signed [N_FRAC:0] y_o, // output for y						
    output wire signed [N_FRAC:0] z_o, // output for z 
    output wire data_out_valid_strobe_o	// strobe that is true if the calaulation is performed and the values are ready to deliver.
);

    localparam ITERATIONS = 6; // defines the amount of rotations. This value is defined by simulation
    localparam BW_SHIFT_VECTOR = 3; // defines the bitwidth if the shift vector

    // The shift vector is precalulated and defines the values for the shift operation in the cordic slice. 
    // The amount of shift vectors is defined from the parameter iterations
    wire [BW_SHIFT_VECTOR-1:0] SHIFT_VECTOR [0:5]; 
    assign SHIFT_VECTOR[0] = 3'b000;
    assign SHIFT_VECTOR[1] = 3'b001;
    assign SHIFT_VECTOR[2] = 3'b010;
    assign SHIFT_VECTOR[3] = 3'b011;
    assign SHIFT_VECTOR[4] = 3'b100;
    assign SHIFT_VECTOR[5] = 3'b101;

    // The angle vector is precalulated and defines the rotation values. 
    // The values a generated from the expression angle_vector = arctan(2^(-i)) where i is the iteration index.
    wire signed [7:0] ANGLES_VECTOR [0:5];
    assign ANGLES_VECTOR[0] = 8'b00100000;
    assign ANGLES_VECTOR[1] = 8'b00010010;
    assign ANGLES_VECTOR[2] = 8'b00001001;
    assign ANGLES_VECTOR[3] = 8'b00000101;
    assign ANGLES_VECTOR[4] = 8'b00000010;
    assign ANGLES_VECTOR[5] = 8'b00000001;

    // states for the state machine
    localparam IDLE_STATE = 2'b00;
    localparam CALCULATION_STATE = 2'b01;
    localparam OUTPUT_STATE = 2'b10;

    localparam BW_COUNTER = $clog2(ITERATIONS); // bitwidth for the iteration counter

    // register variables next_ defines the input for the register and without next_ the actual value is defined
    reg next_data_out_valid_strobe, data_out_valid_strobe;
    reg next_input_select, input_select;
    reg [1:0] next_state, state;
    reg [BW_COUNTER-1 : 0] next_counter_value, counter_value;

    // wires for combinational logic
    wire signed [N_FRAC:0] current_rotation_angle;
    wire [BW_SHIFT_VECTOR-1:0] shift_value;
    reg signed [N_FRAC:0] x_mux, y_mux, z_mux;
    wire signed [N_FRAC:0] x_out, y_out, z_out;

    // registers 
    always @(posedge clk_i) begin
        if (rst_i == 1'b0) begin
            data_out_valid_strobe <= 0;
            counter_value <= 0;
            state <= IDLE_STATE;
            input_select <= 0;
        end else begin
            data_out_valid_strobe <= next_data_out_valid_strobe;
            counter_value <= next_counter_value;
            state <= next_state;
            input_select <= next_input_select;            
        end
    end

    // assign depeding on the current iteration index the rotation angle and the shift value
    assign current_rotation_angle = ANGLES_VECTOR[counter_value];
    assign shift_value = SHIFT_VECTOR[counter_value];

    // instance of the cordic slice to perform a single iteration
    cordic_slice #(.N_FRAC(N_FRAC), .BW_SHIFT_VALUE(BW_SHIFT_VECTOR)) cordic_slice_inst
    (.clk_i(clk_i),
     .rst_i(rst_i),
     .current_rotation_angle_i(current_rotation_angle),
     .shift_value_i(shift_value),
     .x_i(x_mux),
     .y_i(y_mux),
     .z_i(z_mux),
     .x_o(x_out),
     .y_o(y_out),
     .z_o(z_out)
     );

    // combinational logic with a state machine
    always @* begin
        // default assignments
        next_state = state;
        next_data_out_valid_strobe = data_out_valid_strobe;
        next_counter_value = counter_value;
        next_input_select = input_select;

        case (state)
            IDLE_STATE: begin
                // wait until the values are ready for a calulation
                if (data_in_valid_strobe_i == 1'b1) begin
                    next_state = CALCULATION_STATE;
                    next_counter_value = 0;
                    next_input_select = 0; // use the input values for the first calculation
                end
            end 
            CALCULATION_STATE: begin
                // perform the iterations to calculate the desired values
                next_input_select = 1; // use the ouput values of the cordic_slice_inst for the next calulations
                // wait for the state where all iterations are done
                if (counter_value == ITERATIONS-1) begin
                    next_state = OUTPUT_STATE;
                    next_data_out_valid_strobe = 1;
                end else begin
                    next_counter_value = counter_value + 1;
                end
            end
            OUTPUT_STATE: begin
                // perform the output of values from the module
                next_state = IDLE_STATE;
                next_data_out_valid_strobe = 0;
            end
            default:
                // default state should not be entered
                next_state = IDLE_STATE;
        endcase
    end

    // mux for the selection of the input values of the cordic_slice_inst
    always @* begin
        if (input_select == 1'b0) begin
            x_mux = x_i;
            y_mux = y_i;
            z_mux = z_i;
        end else begin
            x_mux = x_out;
            y_mux = y_out;
            z_mux = z_out;
        end
    end

    // assign the register outputs to the outputs of the module
    assign x_o = x_out;
    assign y_o = y_out;
    assign z_o = z_out;
    assign data_out_valid_strobe_o = data_out_valid_strobe;

endmodule

`endif
`default_nettype wire
