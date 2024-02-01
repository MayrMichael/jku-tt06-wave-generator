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

`default_nettype none `timescale 1ns / 1ps

/* This testbench just instantiates the module and makes some convenient wires
   that can be driven / tested by the cocotb test.py.
*/
module tb ();

  // Dump the signals to a VCD file. You can view it with gtkwave.
  initial begin
    $dumpfile("tb.vcd");
    $dumpvars(0, tb);
    #1;
  end

  // Wire up the inputs and outputs:
  reg clk;
  reg rst_n;
  reg ena;
  reg [7:0] ui_in;
  reg [7:0] uio_in;
  wire [7:0] uo_out;
  wire [7:0] uio_out;
  wire [7:0] uio_oe;

  // wires for cocotb
  wire spi_clk, spi_mosi, spi_cs;
  wire [7:0] data_i, data_o;
  wire [1:0] waveform;
  wire enable, set_phase, set_amplitude;

  // wires that are not used
  wire [2:0] not_used = 0;

  // assign the outputs
  assign spi_clk  = uio_out[7];
  assign spi_mosi = uio_out[6];
  assign spi_cs   = uio_out[5];
  assign data_o     = uo_out;

  // assign the inputs
  assign uio_in[0]    = enable;
  assign uio_in[2:1]  = waveform;
  assign uio_in[3]    = set_phase;
  assign uio_in[4]    = set_amplitude;
  assign uio_in[7:5]  = not_used;
  assign ui_in        = data_i;

  tt_um_mayrmichael_wave_generator tt_um_mayrmichael_wave_generator_inst (
  // Include power ports for the Gate Level test:
  `ifdef GL_TEST
      .VPWR(1'b1),
      .VGND(1'b0),
  `endif
      .ui_in  (ui_in),    // Dedicated inputs
      .uo_out (uo_out),   // Dedicated outputs
      .uio_in (uio_in),   // IOs: Input path
      .uio_out(uio_out),  // IOs: Output path
      .uio_oe (uio_oe),   // IOs: Enable path (active high: 0=input, 1=output)
      .ena    (ena),      // enable - goes high when design is selected
      .clk    (clk),      // clock
      .rst_n  (rst_n)     // not reset
  );

endmodule
