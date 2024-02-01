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

`ifndef __SPI_MASTER_ONLY_TX_WITH_SINGLE_CS
`define __SPI_MASTER_ONLY_TX_WITH_SINGLE_CS

`include "spi_master_only_tx.v"

/*
This module extends the spi master module with a cs line
The SPI Master can be configured in one of 4 modes:
    Mode | Clock Polarity (CPOL/CKP) | Clock Phase (CPHA)
     0   |             0             |        0
     1   |             0             |        1
     2   |             1             |        0
     3   |             1             |        1
*/
module spi_master_only_tx_single_cs #(
    parameter SPI_MODE = 0, // defines the mode of the spi master
    parameter CLKS_PER_HALF_BIT = 2, // defines the number of clks per bit devided by 2 (minimum is 2) and corresponds to the frequency of the spi clock. 
    parameter CS_INACTIVE_CLKS = 1 // defines the number of internal clocks cycles after transmitting the byte
) (
    input clk_i, // clock of the system
    input rst_i, // reset (active low) of the system
    input [7:0] data_i, // byte to trasmit
    input data_in_valid_strobe_i, // strobe that identifies a new byte to transmit

    // SPI interface
    output wire spi_clk_o,
    output wire spi_mosi_o,
    output wire spi_cs_o
);
    // states of the state machine
    localparam IDLE        = 2'b00;
    localparam TRANSFER    = 2'b01;
    localparam CS_INACTIVE = 2'b10;

    // register variables next_ defines the input for the register and without next_ the actual value is defined
    reg [1:0] state, next_state; // current state of the state machine register
    reg cs, next_cs; // cs register
    reg cs_inactive_counter, next_cs_inactive_counter; // counter for the inactive cycles

    wire tx_ready; // wire to get the transmit busy signal from the spi master module

    // registers
    always @(posedge clk_i) begin
        if (rst_i == 1'b0) begin
            state <= IDLE;
            cs <= 1'b1;
            cs_inactive_counter <= CS_INACTIVE_CLKS;
        end else begin
            state <= next_state;
            cs <= next_cs;
            cs_inactive_counter <= next_cs_inactive_counter;
        end
    end

    // spi master that controls the clk and the mosi
    spi_master_only_tx  
    #(.SPI_MODE(SPI_MODE),
      .CLKS_PER_HALF_BIT(CLKS_PER_HALF_BIT)
    ) 
    spi_master_only_tx_inst 
    (.clk_i(clk_i),
     .rst_i(rst_i),
     .data_i(data_i), 
     .data_in_valid_strobe_i(data_in_valid_strobe_i), 
     .tx_ready_o(tx_ready),
     .spi_clk_o(spi_clk_o),
     .spi_mosi_o(spi_mosi_o)
    );
    
    // combinational logic with a state machine
    always @* begin
        // default assignments
        next_state = state;
        next_cs = cs;
        next_cs_inactive_counter = cs_inactive_counter;

        case (state)
            IDLE: begin // wait for a new byte to transmit
                if ((data_in_valid_strobe_i & cs) == 1'b1) begin
                    // new byte to transmit
                    next_state = TRANSFER;
                    next_cs = 1'b0;
                end
            end
            TRANSFER: begin // wait for end of transmitting
                if (tx_ready == 1'b1) begin // when tx_ready is again high the spi master module is finished with transmitting
                    next_cs = 1'b1;
                    next_cs_inactive_counter = CS_INACTIVE_CLKS;
                    next_state = CS_INACTIVE;
                end
            end
            CS_INACTIVE: begin // wait some time before a new byte can be transmitted
                if (cs_inactive_counter > 0) begin
                    next_cs_inactive_counter = cs_inactive_counter - 1'b1; 
                end else begin
                    next_state = IDLE;
                end
            end
            default: begin
                next_cs = 1'b1;
                next_state = IDLE;
            end
        endcase
    end

    // assign the register output to the output of the module
    assign spi_cs_o = cs;

endmodule

`endif
`default_nettype wire
