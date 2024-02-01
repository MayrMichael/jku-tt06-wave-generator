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

`ifndef __SPI_MASTER_ONLY_TX
`define __SPI_MASTER_ONLY_TX

/*
This module is an spi master that can only transmit data and has no cs. 
The SPI Master can be configured in one of 4 modes:
    Mode | Clock Polarity (CPOL/CKP) | Clock Phase (CPHA)
     0   |             0             |        0
     1   |             0             |        1
     2   |             1             |        0
     3   |             1             |        1
*/
module spi_master_only_tx #(
    parameter SPI_MODE = 0, // defines the mode of the spi master
    parameter CLKS_PER_HALF_BIT = 2 // defines the number of clks per bit devided by 2 (minimum is 2) and corresponds to the frequency of the spi clock.
) (
    // inputs 
    input clk_i, // clock of the system
    input rst_i, // reset (active low) of the system
    input [7:0] data_i, // byte to trasmit
    input data_in_valid_strobe_i, // strobe that identifies a new byte to transmit
    output wire tx_ready_o, // Transmit Ready for next byte

    // SPI interface
    output wire spi_clk_o,
    output wire spi_mosi_o
);

    wire clk_polarity; // wire that defines the leading edge
    wire clk_phase; // wire that defines the "out" change side
    
    // register variables next_ defines the input for the register and without next_ the actual value is defined
    reg [$clog2(CLKS_PER_HALF_BIT*2)-1:0] spi_clk_counter, next_spi_clk_counter;
    reg spi_clk, next_spi_clk; // register for the spi clock
    reg spi_clk_additional; // additional register to delay the spi clock 
    wire next_spi_clk_additional;

    reg [4:0] spi_clk_edges, next_spi_clk_edges; // counts the edges of the spi signal

    reg leading_edge, next_leading_edge; // register to identify the leading edge
    reg trailing_edge, next_trailing_edge; // register to identify the trailing edge

    reg [2:0] tx_bit_counter, next_tx_bit_counter; // counter for the current bit to send

    reg spi_mosi, next_spi_mosi; // register for the spi mosi
    reg tx_ready, next_tx_ready; // register to identify if the module is currently transmitting

    reg data_in_valid_strobe; // register to delay the strobe 
    wire next_data_in_valid_strobe;

    // CPOL: Clock Polarity
    // CPOL=0 means clock idles at 0, leading edge is rising edge.
    // CPOL=1 means clock idles at 1, leading edge is falling edge.
    assign clk_polarity  = (SPI_MODE == 2) | (SPI_MODE == 3);

    // CPHA: Clock Phase
    // CPHA=0 means the "out" side changes the data on trailing edge of clock
    //              the "in" side captures data on leading edge of clock
    // CPHA=1 means the "out" side changes the data on leading edge of clock
    //              the "in" side captures data on the trailing edge of clock
    assign clk_phase  = (SPI_MODE == 1) | (SPI_MODE == 3);

    // registers
    always @(posedge clk_i) begin
        if (rst_i == 1'b0) begin
            tx_ready <= 0;
            spi_clk_edges <= 0;
            leading_edge <= 0;
            trailing_edge <= 0;
            spi_clk <= clk_polarity;
            spi_clk_counter <= 0;
            spi_mosi <= 1'b0;
            tx_bit_counter <= 3'b111; // send MSb first
            spi_clk_additional  <= clk_polarity;
            data_in_valid_strobe <= 0;
        end else begin
            tx_ready <= next_tx_ready;
            spi_clk_edges <= next_spi_clk_edges;
            leading_edge <= next_leading_edge;
            trailing_edge <= next_trailing_edge;
            spi_clk <= next_spi_clk;
            spi_clk_counter <= next_spi_clk_counter;
            spi_mosi <= next_spi_mosi;
            tx_bit_counter <= next_tx_bit_counter; 
            spi_clk_additional  <= next_spi_clk_additional;
            data_in_valid_strobe <= next_data_in_valid_strobe;
        end
    end

    assign next_spi_clk_additional = spi_clk; // delay the clk by one cycle
    assign next_data_in_valid_strobe = data_in_valid_strobe_i; // delay the strobe by one cycle
    
    // combinational logic for the spi clock and the edges
    always @* begin
        // default assignments
        next_leading_edge = 1'b0; 
        next_trailing_edge = 1'b0;
        next_spi_clk_edges = spi_clk_edges;
        next_spi_clk_counter = spi_clk_counter;
        next_spi_clk = spi_clk;
        next_tx_ready = tx_ready;

        if (data_in_valid_strobe_i == 1'b1) begin // wait for a new sample to receive
            next_tx_ready = 1'b0; // transmitting is busy
            next_spi_clk_edges = 16; // max number of edges by 8 bit
        end else if (spi_clk_edges > 0) begin // start with the spi clock generation
            // transmitting is busy
            next_tx_ready = 1'b0;

            if (spi_clk_counter == CLKS_PER_HALF_BIT*2-1) begin // full spi clock cycle
                next_spi_clk_edges = spi_clk_edges - 1'b1; // edge of spi clock detected
                next_trailing_edge = 1'b1; // define trailing edge
                next_spi_clk_counter = 0; // reset counter
                next_spi_clk = ~spi_clk; // invert spi clock
            end else if (spi_clk_counter == CLKS_PER_HALF_BIT-1) begin // half of the spi clock cycle
                next_spi_clk_edges = spi_clk_edges - 1'b1; // edge of spi clock detected
                next_leading_edge = 1'b1; // define leading edge
                next_spi_clk_counter = spi_clk_counter + 1'b1;
                next_spi_clk = ~spi_clk; // invert spi clock
            end else begin // intermediate step not at an edge in the clock cycle 
                next_spi_clk_counter = spi_clk_counter + 1'b1; 
            end
        end else begin
            // transmitting is not busy
            next_tx_ready = 1'b1;
        end
    end

    // combinational logic for the transmitting 
    always @* begin
        // default assignments
        next_tx_bit_counter = tx_bit_counter;
        next_spi_mosi = spi_mosi;

        if (tx_ready == 1'b1) begin // nothing to transmit
            next_tx_bit_counter = 3'b111;
            next_spi_mosi = 0;
        end else if ((data_in_valid_strobe & ~clk_phase) == 1'b1) begin // start of transmitting
            next_spi_mosi = data_i[3'b111]; // put first bit on the transmit mosi line
            next_tx_bit_counter = 3'b110; // second bit
        end else if ((leading_edge & clk_phase) | (trailing_edge & ~clk_phase) == 1'b1) begin // transmitting
            if (tx_bit_counter > 0) begin // run through all bits to transmit
                next_tx_bit_counter = tx_bit_counter - 1'b1;
            end
            next_spi_mosi = data_i[tx_bit_counter]; // get state of mosi from the current bit to transmit
        end
    end

    // assign the register outputs to the outputs of the module
    assign spi_clk_o = spi_clk_additional;
    assign spi_mosi_o = spi_mosi;
    assign tx_ready_o = tx_ready;
    
endmodule

`endif
`default_nettype wire
