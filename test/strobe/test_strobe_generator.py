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
from test_helper import reset_dut
from cocotb.triggers import ClockCycles, RisingEdge
from cocotb.clock import Clock

DEBUG = False

@cocotb.test()
async def test_strobe_generator(dut):
    """test the strobe generator module if it produces after 40 clock cycles the strobe

    Args:
        dut : strobe_generator module
    """
    # configuration value
    NUMBER_OF_STROBE_TO_GENERATE = 4

    # value from the strobe generator module
    NUMBER_OF_CLKS_TO_WAIT = 40
    
    # init values
    dut.enable_i.value = 0

    # create the clock
    cocotb.start_soon(Clock(dut.clk_i, 10, units="ns").start())

    # reset the dut
    await reset_dut(dut.rst_i, 20)

    # start the strobe generation
    await ClockCycles(dut.clk_i, 1)
    dut.enable_i.value = 1
    await ClockCycles(dut.clk_i, 1)

    # run the test for the strobe 
    for _ in range(NUMBER_OF_STROBE_TO_GENERATE):
        finished = False
        counter = 1
        # run until a strobe appears or the max number of clks is exceeded
        while not finished:
            # wait for the next clock cycle
            await RisingEdge(dut.clk_i)

            # check if the strobe appears
            if dut.strobe_o.value.binstr == '1':
                if DEBUG:
                    dut._log.info(f'#{counter:>03} -> {dut.strobe_o.value.binstr}')
                finished = True
                # check if the strobe appeared on the right position
                if counter != NUMBER_OF_CLKS_TO_WAIT:
                    assert False, f'Strobe did not appear after {NUMBER_OF_CLKS_TO_WAIT} clock cylces'

            # pretend a infinity loop
            if counter > NUMBER_OF_CLKS_TO_WAIT:
                assert False, f'Strobe did not appear after {NUMBER_OF_CLKS_TO_WAIT} clock cylces'

            counter += 1

    dut._log.info('Test finished')