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
import vp_cordic_iterative
import vp_sin_generator
from test_helper import reset_dut, frac2bin, unsigned2bin
from cocotb.triggers import Timer, FallingEdge, ClockCycles, RisingEdge, Join, First 
from cocotb.clock import Clock

DEBUG = False

@cocotb.test()
async def cosim_tb_sinus_part(dut):
    """cosim to test the bitwise truth of the sinus output of the verilog implementation of the tb (tt_um_mayrmichael_wave_generator) against the python virtual prototype of the sin_generator implementation

    Args:
        dut : tb of the tt_um_mayrmichael_wave_generator module
    """

    # general values for the cosim
    ITERATIONS = 6
    Q = 7
    PHASE = 0.308807373046875
    NUMBER_OF_SAMPLES = 300
    SINUS_MODE = 0

    # run the virtual prototype
    calc_values, xc_values, yc_values, zc_values, xi_values, yi_values, zi_values = vp_sin_generator.sin_gen_debug(Q, PHASE, ITERATIONS, NUMBER_OF_SAMPLES)

    # init values for the dut
    dut.ena.value = 1
    dut.enable.value = 0
    dut.set_phase.value = 0
    dut.set_amplitude.value = 0
    dut.waveform.value = unsigned2bin(SINUS_MODE, 2)
    dut.data_i.value = frac2bin(0, Q)

    # start the clock
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())

    # reset the dut
    await reset_dut(dut.rst_n, 20)

    # set the phase of the dut
    await RisingEdge(dut.clk)
    dut.data_i.value = frac2bin(PHASE, Q)
    dut.set_phase.value = 1
    await RisingEdge(dut.clk)
    dut.set_phase.value = 0

    # set the amplitude of the dut
    await RisingEdge(dut.clk)
    dut.data_i.value = frac2bin(xi_values[0], Q)
    dut.set_amplitude.value = 1
    await RisingEdge(dut.clk)
    dut.set_amplitude.value = 0
    
    # enable the output sample generation of the dut
    dut.enable.value = 1

    # start the checker and a enable control that tests the enable input
    forked = cocotb.start_soon(check_value(dut, calc_values, Q))
    await cocotb.start_soon(enable_control(dut))

    # wait for the moment where all samples are checked
    await Join(forked)

    if DEBUG:
        dut._log.info('Test finished')

async def check_value(dut, calc_values, Q):
    """Checks the values of the dut against the values from the virtual prototype

    Args:
        dut : tb of the tt_um_mayrmichael_wave_generator module
        calc_values (np.array): values from the virtual prototype
        Q (int): used fraction number notation
    """
    if DEBUG:
        dut._log.info(f'#{0:>03} -> {"dut".center(8)} | {"python".center(8)}')
    
    for i in range(len(calc_values)):

        # wait for the falling spi cs pin that indicates a new calculated sample
        await FallingEdge(dut.spi_cs)
        
        if DEBUG:
            dut._log.info(f'#{i:>03} -> {dut.data_o.value.binstr} | {frac2bin(calc_values[i], Q).binstr}')

        # check the parallel data output against the virtual prototype value
        assert dut.data_o.value.binstr == frac2bin(calc_values[i], Q).binstr

        # check the serial data output against the virtual prototype value
        sample_str = frac2bin(calc_values[i], Q)
        for k in range(8):
            t1 = RisingEdge(dut.spi_clk)
            t2 = RisingEdge(dut.spi_cs)
            t_ret = await First(t1, t2)
            # check that is implemented to check if the cs line is always low during the serial data transfer
            if t_ret is t2:
                assert False
            
            if DEBUG:
                dut._log.info(f'----- #{k:>03} -> {dut.spi_mosi.value.binstr}  | {sample_str[k].binstr}')
            
            # check the serial output values
            assert dut.spi_mosi.value.binstr == sample_str[k].binstr
            assert dut.spi_cs.value == 0

        # wait for the end of the transmitting
        await RisingEdge(dut.spi_cs)

async def enable_control(dut):
    """This method should test the enable port of the wave_generator. This is done by deactivating
       the enable port after some time. Therefore no new value should be printed out. After some time the enable port 
       is set high again to test the other output samples 

    Args:
        dut : tb of the tt_um_mayrmichael_wave_generator module
    """
    await Timer(2000, units='ns')
    dut.enable.value = 0
    await ClockCycles(dut.clk, 70)
    dut.enable.value = 1




