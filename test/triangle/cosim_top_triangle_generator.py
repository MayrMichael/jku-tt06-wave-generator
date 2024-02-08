# Copyright 2024 Michael Mayr
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE−2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# imports
import cocotb
import numpy as np
import vp_triangle
import vp_square_puls
from test_helper import reset_dut, frac2bin
from cocotb.triggers import FallingEdge, RisingEdge
from cocotb.clock import Clock

DEBUG = False    

@cocotb.test()
async def cosim_top_triangle_generator_sawtooth_part(dut):
    """cosim to test the bitwise truth of the sawtooth output of the verilog implementation of the top_triangle_generator against the python virtual prototype of the triangle implementation

    Args:
        dut : top_triangle_generator module
    """
    # general values for the cosim
    Q = 7
    PHASE = 0.01
    NUMBER_OF_SAMPLES = 1000

    # specify the amplitude value
    lsb = 2**(-Q)
    amplitude = 1 - 40 * lsb

    # quantize the values
    phase_quantized = vp_triangle.quantize_value(PHASE, lsb)
    amplitude_quantized = vp_triangle.quantize_value(amplitude, lsb)

    # run the virtual prototype
    calc_values = vp_triangle.sawtooth(Q, phase_quantized, amplitude_quantized, NUMBER_OF_SAMPLES)

    # init values for the dut
    dut.overflow_mode_i.value = 0
    dut.get_next_data_strobe_i.value = 0
    dut.phase_i.value = frac2bin(phase_quantized, Q)
    dut.amplitude_i.value = frac2bin(amplitude_quantized, Q)

    # start the clock
    cocotb.start_soon(Clock(dut.clk_i, 10, units="ns").start())

    # reset the dut
    await reset_dut(dut.rst_i, 20)

    if DEBUG:
        dut._log.info(f'#{0:>03} -> {"dut".center(8)} | {"python".center(8)}')
    
    # check the verilog implementation against the virtual prototype
    for i in range(NUMBER_OF_SAMPLES):
        # request the next sample
        await FallingEdge(dut.clk_i)
        dut.get_next_data_strobe_i.value = 1

        # wait for the next output sample
        await RisingEdge(dut.data_sawtooth_out_valid_strobe_o)
        dut.get_next_data_strobe_i.value = 0

        if DEBUG:
            if dut.data_sawtooth_o.value.binstr != frac2bin(calc_values[i], Q).binstr:
                dut._log.info(f'#{i:>03} -> {dut.data_sawtooth_o.value.binstr} | {frac2bin(calc_values[i], Q).binstr}')

        # check the output sample against the virtual prototype
        assert dut.data_sawtooth_o.value.binstr == frac2bin(calc_values[i], Q).binstr

        await FallingEdge(dut.clk_i)
    
    dut._log.info('Test finished')
    

@cocotb.test()
async def cosim_top_triangle_generator_triangle_part(dut):
    """cosim to test the bitwise truth of the triangle output of the verilog implementation of the top_triangle_generator against the python virtual prototype of the triangle implementation

    Args:
        dut : top_triangle_generator module
    """
    # general values for the cosim
    Q = 7
    PHASE = 0.01
    NUMBER_OF_SAMPLES = 1000

    # specify the amplitude value
    lsb = 2**(-Q)
    amplitude = 1 - 40 * lsb

    # quantize the values
    phase_quantized = vp_triangle.quantize_value(PHASE, lsb)
    amplitude_quantized = vp_triangle.quantize_value(amplitude, lsb)

    # run the virtual prototype
    calc_values = vp_triangle.triangle(Q, phase_quantized, amplitude_quantized, NUMBER_OF_SAMPLES)

    # init values for the dut
    dut.overflow_mode_i.value = 0
    dut.get_next_data_strobe_i.value = 0
    dut.phase_i.value = frac2bin(phase_quantized, Q)
    dut.amplitude_i.value = frac2bin(amplitude_quantized, Q)

    # start the clock
    cocotb.start_soon(Clock(dut.clk_i, 10, units="ns").start())

    # reset the dut
    await reset_dut(dut.rst_i, 20)

    if DEBUG:
        dut._log.info(f'#{0:>03} -> {"dut".center(8)} | {"python".center(8)}')
    
    # check the verilog implementation against the virtual prototype
    for i in range(NUMBER_OF_SAMPLES):
        # request the next sample
        await FallingEdge(dut.clk_i)
        dut.get_next_data_strobe_i.value = 1
        await FallingEdge(dut.clk_i)
        dut.get_next_data_strobe_i.value = 0

        # wait for the next output sample
        await RisingEdge(dut.data_triangle_out_valid_strobe_o)

        if DEBUG:
            if dut.data_triangle_o.value.binstr != frac2bin(calc_values[i], Q).binstr:
                dut._log.info(f'#{i:>03} -> {dut.data_triangle_o.value.binstr} | {frac2bin(calc_values[i], Q).binstr}')

        # check the output sample against the virtual prototype
        assert dut.data_triangle_o.value.binstr == frac2bin(calc_values[i], Q).binstr
   
    
    dut._log.info('Test finished')


@cocotb.test()
async def cosim_top_triangle_generator_square_puls_part(dut):
    """cosim to test the bitwise truth of the square_puls output of the verilog implementation of the top_triangle_generator against the python virtual prototype of the square puls implementation

    Args:
        dut : top_triangle_generator module
    """
    # general values for the cosim
    Q = 7
    PHASE = 0.1
    THRESHOLD = 0.1
    NUMBER_OF_SAMPLES = 1000

    # quantize the values
    lsb = 2**(-Q)
    phase_quantized = vp_square_puls.quantize_value(PHASE, lsb)
    threshold_quantized = vp_square_puls.quantize_value(THRESHOLD, lsb)

    # run the virtual prototype
    calc_values = vp_square_puls.square_puls(Q, phase_quantized, threshold_quantized, NUMBER_OF_SAMPLES)

    # init values for the dut
    dut.overflow_mode_i.value = 1
    dut.get_next_data_strobe_i.value = 0
    dut.phase_i.value = frac2bin(phase_quantized, Q)
    dut.amplitude_i.value = frac2bin(threshold_quantized, Q)

    # start the clock
    cocotb.start_soon(Clock(dut.clk_i, 10, units="ns").start())

    # reset the dut
    await reset_dut(dut.rst_i, 20)

    if DEBUG:
        dut._log.info(f'#{0:>03} -> {"dut".center(8)} | {"python".center(8)}')
    
    # check the verilog implementation against the virtual prototype
    for i in range(NUMBER_OF_SAMPLES):
        # request the next sample
        await FallingEdge(dut.clk_i)
        dut.get_next_data_strobe_i.value = 1
        await FallingEdge(dut.clk_i)
        dut.get_next_data_strobe_i.value = 0

        # wait for the next output sample
        await RisingEdge(dut.data_square_puls_out_valid_strobe_o)

        if DEBUG:
            if dut.data_square_puls_o.value.binstr != frac2bin(calc_values[i], Q).binstr:
                dut._log.info(f'#{i:>03} -> {dut.data_square_puls_o.value.binstr} | {frac2bin(calc_values[i], Q).binstr}')

        # check the output sample against the virtual prototype
        assert dut.data_square_puls_o.value.binstr == frac2bin(calc_values[i], Q).binstr
   
    
    dut._log.info('Test finished')