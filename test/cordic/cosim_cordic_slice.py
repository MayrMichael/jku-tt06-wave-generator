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
from test_helper import reset_dut, frac2bin, unsigned2bin
from cocotb.triggers import RisingEdge, ClockCycles
from cocotb.clock import Clock

DEBUG = False

@cocotb.test()
async def cosim_cordic_slice(dut):
    """ cosim to test the bitwise truth of the verilog implementation of the cordic_slice against the python virtual prototype of the cordic_iterative implementation

    Args:
        dut : cordic_slice dut
    """
    # general values for the cosim
    CORDIC_ITERATIONS = 15
    Q = 15
    BW_SHIFT_VALUE = 4
    PHASE = 0.308807373046875

    # generate the needed values for the cordic algorithm
    lsb = 2**(-Q)
    shift_vector = vp_cordic_iterative.gen_shift_vector(CORDIC_ITERATIONS)
    k = vp_cordic_iterative.gen_k(shift_vector, lsb)
    angles_vector = vp_cordic_iterative.gen_angles_vector(shift_vector, lsb)

    # generate the input values
    xi = vp_cordic_iterative.quantize_value(1.0 - lsb, lsb)
    xi = vp_cordic_iterative.quantize_value(xi * k, lsb)
    xi = vp_cordic_iterative.quantize_value(xi - lsb, lsb)
    yi = vp_cordic_iterative.quantize_value(0, lsb)
    zi = vp_cordic_iterative.quantize_value(PHASE, lsb)

    # run the virtual prototype
    xo, yo, zo = vp_cordic_iterative.cordic(xi,yi,zi, angles_vector,  shift_vector, CORDIC_ITERATIONS, Q)

    # setting up the cordic slice module
    dut.current_rotation_angle_i.value = frac2bin(angles_vector[0], Q)
    dut.shift_value_i.value = unsigned2bin(shift_vector[0], BW_SHIFT_VALUE)
    dut.x_i.value = frac2bin(xi, Q)
    dut.y_i.value = frac2bin(yi, Q)
    dut.z_i.value = frac2bin(zi, Q)

    # start the clock
    cocotb.start_soon(Clock(dut.clk_i, 10, units="ns").start())

    # reset the dut
    await reset_dut(dut.rst_i, 20)

    # run the cordic_slice against the cordic_iterations of the vp
    for i in range(CORDIC_ITERATIONS):
        
        # set the input values
        await RisingEdge(dut.clk_i)
        dut.current_rotation_angle_i.value = frac2bin(angles_vector[i], Q)
        dut.shift_value_i.value = unsigned2bin(shift_vector[i], BW_SHIFT_VALUE)
        dut.x_i.value = frac2bin(xo[i], Q)
        dut.y_i.value = frac2bin(yo[i], Q)
        dut.z_i.value = frac2bin(zo[i], Q)
        
        await ClockCycles(dut.clk_i, 2)
        
        # check the results against the vp
        assert dut.z_o.value.binstr == frac2bin(zo[i + 1], Q).binstr
        assert dut.y_o.value.binstr == frac2bin(yo[i + 1], Q).binstr
        assert dut.x_o.value.binstr == frac2bin(xo[i + 1], Q).binstr
        
        if DEBUG:
            dut._log.info(f'Iteration {i+1}/{CORDIC_ITERATIONS} passed')

        await ClockCycles(dut.clk_i, 2)
    
    dut._log.info('Test finished')
    

