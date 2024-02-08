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
from test_helper import reset_dut, frac2bin
from cocotb.triggers import Timer, FallingEdge, RisingEdge
from cocotb.clock import Clock

DEBUG = False

@cocotb.test()
async def cosim_sin_generator(dut):
    """cosim to test the bitwise truth of the verilog implementation of the sin_generator against the python virtual prototype of the sin_generator implementation

    Args:
        dut : sin_generator dut
    """
    # general values for the cosim
    CORDIC_ITERATIONS = 6 
    Q7 = 7
    PHASE = 0.308807373046875
    NUMBER_OF_SAMPLES = 300

    # run the virtual prototype
    calc_values, xc_values, yc_values, zc_values, xi_values, yi_values, zi_values = vp_sin_generator.sin_gen_debug(Q7, PHASE, CORDIC_ITERATIONS, NUMBER_OF_SAMPLES)

    # setup the inputs of the sin_generator
    dut.get_next_data_strobe_i.value = 0
    dut.phase_i.value = frac2bin(PHASE, Q7)
    dut.amplitude_i.value = frac2bin(xi_values[0], Q7)

    # start the clock
    cocotb.start_soon(Clock(dut.clk_i, 10, units="ns").start())

    # reset the dut
    await reset_dut(dut.rst_i, 20)

    await FallingEdge(dut.clk_i)

    if DEBUG:
        dut._log.info(f'#{0:>03} -> {"dut".center(8)} | {"python".center(8)}')

    for i in range(NUMBER_OF_SAMPLES):
        # request new sample
        await FallingEdge(dut.clk_i)
        dut.get_next_data_strobe_i.value = 1
        await RisingEdge(dut.phase_increment_done_strobe)
        dut.get_next_data_strobe_i.value = 0

        if DEBUG:
            dut._log.info('----------------------- input convergence ----------------------------------')
            dut._log.info(f'{dut.amplitude.value.binstr} | {dut.y_const.value.binstr} | {dut.z_phase.value.binstr} | dut')
            dut._log.info(f'{frac2bin(xi_values[i], Q7).binstr} | {frac2bin(yi_values[i], Q7).binstr} | {frac2bin(zi_values[i], Q7).binstr} | python')
        
        # test the inputs of the module
        assert dut.amplitude_i.value.binstr == frac2bin(xi_values[i], Q7).binstr
        assert dut.y_const.value.binstr == frac2bin(yi_values[i], Q7).binstr
        assert dut.z_phase.value.binstr == frac2bin(zi_values[i], Q7).binstr

        if DEBUG:
            dut._log.info('-------------------------------------------------------------------------------')

        await RisingEdge(dut.data_con_out_valid_strobe)

        if DEBUG:
            dut._log.info('----------------------- output convergence ----------------------------------')
            dut._log.info(f'{dut.x_con_out.value.binstr} | {dut.y_con_out.value.binstr} | {dut.z_con_out.value.binstr} | dut')
            dut._log.info(f'{frac2bin(xc_values[i], Q7, FRAC_BITS).binstr} | {frac2bin(yc_values[i], Q7, FRAC_BITS).binstr} | {frac2bin(zc_values[i], Q7, FRAC_BITS).binstr} | python')
        
        # test the values after the convergence unit in the sin_generator
        assert dut.x_con_out.value.binstr == frac2bin(xc_values[i], Q7).binstr
        assert dut.y_con_out.value.binstr == frac2bin(yc_values[i], Q7).binstr
        assert dut.z_con_out.value.binstr == frac2bin(zc_values[i], Q7).binstr
        
        if DEBUG:
            dut._log.info('-------------------------------------------------------------------------------')

        await RisingEdge(dut.data_out_valid_strobe_o)
        await Timer(10, units='ps')
        
        if DEBUG:
            dut._log.info(f'#{i:>03} -> {dut.data_o.value.binstr} | {frac2bin(calc_values[i], Q7).binstr}')

        # test the output value of the sin_generator
        assert dut.data_o.value.binstr == frac2bin(calc_values[i], Q7).binstr
   
    dut._log.info('Test finished')
    

