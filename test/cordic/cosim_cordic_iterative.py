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
from test_helper import reset_dut, frac2bin
from cocotb.triggers import FallingEdge, RisingEdge
from cocotb.clock import Clock

DEBUG = False

@cocotb.test()
async def cosim_cordic_iterative(dut):
    """ cosim to test the bitwise truth of the verilog implementation of the cordic_iterative against the python virtual prototype of the cordic_iterative implementation

    Args:
        dut : cordic_iterative dut
    """
    # general values for the cosim
    CORDIC_ITERATIONS = 6
    Q7 = 7
    PHASE = 0.308807373046875
    NUMBER_OF_TESTS = 30
    
    # generate the needed values for the cordic iterations
    lsb = 2**(-Q7)
    shift_vector = vp_cordic_iterative.gen_shift_vector(CORDIC_ITERATIONS)
    k = vp_cordic_iterative.gen_k(shift_vector, lsb) # length compensation for the iterations
    angles_vector = vp_cordic_iterative.gen_angles_vector(shift_vector, lsb)

    # setup the inputs of the cordic iterative algorithm
    # to get a sin output we set yi = 0 and xi to 1 multiplied with the length compensation that is needed because of the algorithm
    xi = vp_cordic_iterative.quantize_value(1.0 - lsb, lsb)
    xi = vp_cordic_iterative.quantize_value(xi * k, lsb)
    xi = vp_cordic_iterative.quantize_value(xi - lsb, lsb)
    yi = vp_cordic_iterative.quantize_value(0, lsb)
    zi = vp_cordic_iterative.quantize_value(PHASE, lsb)

    # storage for the comparision between vp and verilog module
    x_input = np.zeros(NUMBER_OF_TESTS)
    y_input = np.zeros(NUMBER_OF_TESTS)
    z_input = np.zeros(NUMBER_OF_TESTS)
    x_calc_vp = np.zeros(NUMBER_OF_TESTS)
    y_calc_vp = np.zeros(NUMBER_OF_TESTS)
    z_calc_vp = np.zeros(NUMBER_OF_TESTS)

    # run the virtual prototype
    for i in range(NUMBER_OF_TESTS):
        xo, yo, zo = vp_cordic_iterative.cordic(xi,yi,zi, angles_vector, shift_vector, CORDIC_ITERATIONS, Q7)

        # store for comparison
        x_input[i] = xi
        y_input[i] = yi
        z_input[i] = zi
        x_calc_vp[i] = xo[CORDIC_ITERATIONS]
        y_calc_vp[i] = yo[CORDIC_ITERATIONS]
        z_calc_vp[i] = zo[CORDIC_ITERATIONS]

        # generate next zi for another test round
        zi = vp_cordic_iterative.quantize_value(zi + PHASE, lsb)

    # setting up the cordic_iterative module 
    dut.x_i.value = frac2bin(x_input[0], Q7)
    dut.y_i.value = frac2bin(y_input[0], Q7)
    dut.z_i.value = frac2bin(z_input[0], Q7)
    dut.data_in_valid_strobe_i.value = 0

    # start the clock
    cocotb.start_soon(Clock(dut.clk_i, 10, units="ns").start())

    # reset the dut
    await reset_dut(dut.rst_i, 20)

    # run the verilog module
    for i in range(NUMBER_OF_TESTS):
        if DEBUG:
            dut._log.info(f'Test {i}: zi = {frac2bin(z_input[i], Q7).binstr}')

        # start the algorithm
        await FallingEdge(dut.clk_i)
        dut.data_in_valid_strobe_i.value = 1
        await FallingEdge(dut.clk_i)
        dut.data_in_valid_strobe_i.value = 0

        # wait for a result of the module
        await RisingEdge(dut.data_out_valid_strobe_o)

        # check the results against the vp results
        assert dut.x_o.value.binstr == frac2bin(x_calc_vp[i], Q7).binstr
        assert dut.y_o.value.binstr == frac2bin(y_calc_vp[i], Q7).binstr
        assert dut.z_o.value.binstr == frac2bin(z_calc_vp[i], Q7).binstr
        
        # wait to setup the next test round
        await FallingEdge(dut.data_out_valid_strobe_o)

        # set new values ignore on the last test round
        if i < NUMBER_OF_TESTS-1:
            dut.x_i.value = frac2bin(x_input[i + 1], Q7)
            dut.y_i.value = frac2bin(y_input[i + 1], Q7)
            dut.z_i.value = frac2bin(z_input[i + 1], Q7)
    
    dut._log.info('Test finished')
    
