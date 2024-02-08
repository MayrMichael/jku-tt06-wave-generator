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
import vp_cordic_iterative
import vp_sin_generator 
from test_helper import reset_dut, frac2bin, unsigned2bin
from cocotb.triggers import Timer, ClockCycles, RisingEdge, Join
from cocotb.clock import Clock

DEBUG = False

@cocotb.test()
async def cosim_wave_generator(dut):
    """cosim to test the bitwise truth of the sinus output of the verilog implementation of the wave_generator against the python virtual prototype of the sin_generator implementation

    Args:
        dut (_type_): wave_generator dut
    """
    # general values for the cosim
    CORDIC_ITERATIONS = 6
    Q = 7
    PHASE = 0.308807373046875
    SINUS_MODE = 0
    NUMBER_OF_SAMPLES = 300

    # run the virtual prototype
    calc_values, xc_values, yc_values, zc_values, xi_values, yi_values, zi_values = vp_sin_generator.sin_gen_debug(Q, PHASE, CORDIC_ITERATIONS, NUMBER_OF_SAMPLES)

    # init values for dut
    dut.enable_i.value = 0
    dut.set_phase_strobe_i.value = 0
    dut.set_amplitude_strobe_i.value = 0
    dut.waveform_i.value = unsigned2bin(SINUS_MODE, 2)
    dut.data_i.value = frac2bin(0, Q)

    # start the clock
    cocotb.start_soon(Clock(dut.clk_i, 10, units="ns").start())

    # reset the dut
    await reset_dut(dut.rst_i, 20)

    # set the phase of the dut
    await RisingEdge(dut.clk_i)
    dut.data_i.value = frac2bin(PHASE, Q)
    dut.set_phase_strobe_i.value = 1
    await RisingEdge(dut.clk_i)
    dut.set_phase_strobe_i.value = 0

    # set the amplitude of the dut
    await RisingEdge(dut.clk_i)
    dut.data_i.value = frac2bin(xi_values[0], Q)
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
        dut : wave_generator dut
        calc_values (np.array): values from the virtual prototype
        Q (int): used fraction number notation
    """
    if DEBUG:
        dut._log.info(f'#{0:>03} -> {"dut".center(8)} | {"python".center(8)}')
    
    # run through all pre calculated values of the virtual prototype
    for i in range(len(calc_values)):
        # wait for a new output sample
        await RisingEdge(dut.data_valid_strobe_o)
        
        if DEBUG:
            dut._log.info(f'#{i:>03} -> {dut.data_o.value.binstr} | {frac2bin(calc_values[i], Q).binstr}')

        # check the given output sample against the virtual prototype value
        assert dut.data_o.value.binstr == frac2bin(calc_values[i], Q).binstr

async def enable_control(dut):
    """This method should test the enable port of the wave_generator. This is done by deactivating
       the enable port after some time. Therefore no new value should be printed out. After some time the enable port 
       is set high again to test the other output samples 

    Args:
        dut : wave_generator dut
    """
    await Timer(150, units='ns')
    dut.enable_i.value = 0
    await ClockCycles(dut.clk_i, 70)
    dut.enable_i.value = 1

    

