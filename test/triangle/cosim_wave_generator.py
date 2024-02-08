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
from test_helper import frac2bin, unsigned2bin, reset_dut
from cocotb.triggers import Timer, ClockCycles, RisingEdge, Join
from cocotb.clock import Clock

DEBUG = False

@cocotb.test()
async def cosim_wave_generator_sawtooth_part(dut):
    """cosim to test the bitwise truth of the sawtooth output of the verilog implementation of the wave_generator against the python virtual prototype of the triangle implementation

    Args:
        dut : wave_generator module
    """
    # general values for the cosim
    Q = 7
    PHASE = 0.01
    NUMBER_OF_SAMPLES = 1000
    SAWTOOTH_MODE = 2

    # specify the amplitude value
    lsb = 2**(-Q)
    amplitude = 1 - 40 * lsb

    # quantize the values
    phase_quantized = vp_triangle.quantize_value(PHASE, lsb)
    amplitude_quantized = vp_triangle.quantize_value(amplitude, lsb)

    # run the virtual prototype
    calc_values = vp_triangle.sawtooth(Q, phase_quantized, amplitude_quantized, NUMBER_OF_SAMPLES)

    # run the verilog implementation
    run_module(dut, SAWTOOTH_MODE, phase_quantized, amplitude, Q, calc_values)


@cocotb.test()
async def cosim_wave_generator_triangle_part(dut):
    """cosim to test the bitwise truth of the triangle output of the verilog implementation of the wave_generator against the python virtual prototype of the triangle implementation

    Args:
        dut : wave_generator module
    """
    # general values for the cosim
    Q = 7
    PHASE = 0.01
    NUMBER_OF_SAMPLES = 1000
    TRIANGLE_MODE = 3

    # specify the amplitude value
    lsb = 2**(-Q)
    amplitude = 1 - 40 * lsb

    # quantize the values
    phase_quantized = vp_triangle.quantize_value(PHASE, lsb)
    amplitude_quantized = vp_triangle.quantize_value(amplitude, lsb)

    # run the virtual prototype
    calc_values = vp_triangle.triangle(Q, phase_quantized, amplitude_quantized, NUMBER_OF_SAMPLES)

    # run the verilog implementation
    run_module(dut, TRIANGLE_MODE, phase_quantized, amplitude_quantized, Q, calc_values)

@cocotb.test()
async def cosim_wave_generator_square_puls_part(dut):
    """cosim to test the bitwise truth of the square puls output of the verilog implementation of the wave_generator against the python virtual prototype of the square pulse implementation

    Args:
        dut : wave_generator module
    """
    # general values for the cosim
    Q = 7
    PHASE = 0.1
    THRESHOLD = 0.2
    NUMBER_OF_SAMPLES = 1000
    SQUARE_PULSE_MODE = 1

    # quantize the values
    lsb = 2**(-Q)
    phase_quantized = vp_square_puls.quantize_value(PHASE, lsb)
    threshold_quantized = vp_square_puls.quantize_value(THRESHOLD, lsb)

    # run the virtual prototype
    calc_values = vp_square_puls.square_puls(Q, phase_quantized, threshold_quantized, NUMBER_OF_SAMPLES)

    # run the verilog implementation
    run_module(dut, SQUARE_PULSE_MODE, phase_quantized, threshold_quantized, Q, calc_values)

async def run_module(dut, mode, phase, amplitude, Q, calc_values):
    """This function runs the tests on the verilog module

    Args:
        dut : wave_generator module
        mode (int): defines the output wave of the module
        phase (float): phase that should be used 
        amplitude (float): amplitude value that should be used
        Q (int): used fraction number notation
        calc_values (np.array): values from the virtual prototype
    """
    # init values for dut
    dut.enable_i.value = 0
    dut.set_phase_strobe_i.value = 0
    dut.set_amplitude_strobe_i.value = 0
    dut.waveform_i.value = unsigned2bin(mode, 2) 
    dut.data_i.value = frac2bin(0, Q)

    # start the clock
    cocotb.start_soon(Clock(dut.clk_i, 10, units="ns").start())

    # reset the dut
    await reset_dut(dut.rst_i, 20)

    # set the phase of the dut
    await RisingEdge(dut.clk_i)
    dut.data_i.value = frac2bin(phase, Q)
    dut.set_phase_strobe_i.value = 1
    await RisingEdge(dut.clk_i)
    dut.set_phase_strobe_i.value = 0

    # set the amplitude of the dut
    await RisingEdge(dut.clk_i)
    dut.data_i.value = frac2bin(amplitude, Q)
    dut.set_amplitude_strobe_i.value = 1
    await RisingEdge(dut.clk_i)
    dut.set_amplitude_strobe_i.value = 0
    
    # enable the output sample generation of the dut
    dut.enable_i.value = 1

    # start the checker and a enable control that tests the enable input
    forked = cocotb.start_soon(check_value(dut, calc_values, Q))
    await cocotb.start_soon(enable_control(dut))

    # wait for the moment where all samples are checked
    await Join(forked)
    
    dut._log.info('Test finished')

async def check_value(dut, calc_values, Q):
    """Checks the values of the dut against the values from the virtual prototype

    Args:
        dut : wave generator module
        calc_values (np.array): values from the virtual prototype
        Q (int): used fraction number notation
    """
    if DEBUG:
        dut._log.info(f'#{0:>03} -> {"dut".center(8)} | {"python".center(8)}')
    
    for i in range(len(calc_values)):
        # wait for the next output sample
        await RisingEdge(dut.data_valid_strobe_o)
        
        if DEBUG:
            dut._log.info(f'#{i:>03} -> {dut.data_o.value.binstr} | {frac2bin(calc_values[i], Q).binstr}')

        # check the output sample against the virtual prototype value
        assert dut.data_o.value.binstr == frac2bin(calc_values[i], Q).binstr


async def enable_control(dut):
    """This method should test the enable port of the wave_generator. This is done by deactivating
       the enable port after some time. Therefore no new value should be printed out. After some time the enable port 
       is set high again to test the other output samples 

    Args:
        dut : tb of the tt_um_mayrmichael_wave_generator module
    """
    await Timer(150, units='ns')
    dut.enable_i.value = 0
    await ClockCycles(dut.clk_i, 70)
    dut.enable_i.value = 1
    