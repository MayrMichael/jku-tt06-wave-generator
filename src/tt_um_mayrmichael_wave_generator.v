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

`include "wave_generator.v"
`include "spi_master_only_tx_single_cs.v"

module tt_um_mayrmichael_wave_generator (
    input  wire [7:0] ui_in,    // Dedicated inputs 
    output wire [7:0] uo_out,   // Dedicated outputs
    input  wire [7:0] uio_in,   // IOs: Bidirectional Input path
    output wire [7:0] uio_out,  // IOs: Bidirectional Output path
    output wire [7:0] uio_oe,   // IOs: Bidirectional Enable path (active high: 0=input, 1=output)
    input  wire       ena,      // will go high when the design is enabled
    input  wire       clk,      // clock
    input  wire       rst_n     // reset_n - low to reset
);
    wire data_valid_strobe;
    wire [7:0] data;

    wire set_phase, set_amplitude;

    wire [7:0] set_phase_amplitude_value;
    wire enable;
    wire [1:0] waveform;

    /* verilator lint_off UNUSEDSIGNAL */
    wire [2:0] not_used;
    /* verilator lint_on UNUSEDSIGNAL */

    assign set_phase_amplitude_value = ui_in;
    
    assign uo_out = data;

    assign uio_oe = 8'b11100000;
    assign uio_out[7] = spi_clk;
    assign uio_out[6] = spi_mosi;
    assign uio_out[5] = spi_cs;

    assign uio_out[4:0] = 5'b00000;

    assign enable = uio_in[0] & ena;
    assign waveform = uio_in[2:1];
    assign set_phase = uio_in[3];
    assign set_amplitude = uio_in[4];
    assign not_used = uio_in[7:5];

    wire spi_clk;
    wire spi_mosi;
    wire spi_cs;

    spi_master_only_tx_single_cs spi_master_only_tx_single_cs_inst
    (
    .clk_i(clk),
    .rst_i(rst_n),
    .data_i(data), 
    .data_in_valid_strobe_i(data_valid_strobe), 
    .spi_clk_o(spi_clk),
    .spi_mosi_o(spi_mosi),
    .spi_cs_o(spi_cs)
    );

    wave_generator wave_generator_inst
    (
    .clk_i(clk),
    .rst_i(rst_n),
    .enable_i(enable),
    .waveform_i(waveform),
    .set_phase_strobe_i(set_phase),
    .set_amplitude_strobe_i(set_amplitude),
    .data_i(set_phase_amplitude_value),
    .data_o(data),
    .data_valid_strobe_o(data_valid_strobe)
    );

endmodule

