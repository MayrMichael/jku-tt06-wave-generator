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
from cocotb.triggers import FallingEdge, ClockCycles, RisingEdge, Join, First
from cocotb.clock import Clock
from test_helper import reset_dut, unsigned2bin

@cocotb.test()
async def test_spi_master_only_tx_single_cs(dut):
    """test the spi_master_only_tx_single_cs module if it produces the right serial transmission

    Args:
        dut : spi_master_only_tx_single_cs module
    """
    # generate values for testing
    n_samples = 16
    samples = list(range(n_samples))
    samples.extend([128, 255, 128, 255, 0, 85])
    
    # init values for the dut
    dut.data_in_valid_strobe_i.value = 0
    dut.data_i.value = unsigned2bin(0, 8)

    # start the clock
    cocotb.start_soon(Clock(dut.clk_i, 10, units="ns").start())

    # reset the dut
    await reset_dut(dut.rst_i, 20)

    await ClockCycles(dut.clk_i, 1)

    # check the generated samples
    for n in samples:
        # load the sample
        dut.data_in_valid_strobe_i.value = 1
        dut.data_i.value = unsigned2bin(n, 8)
        await ClockCycles(dut.clk_i, 1)
        dut.data_in_valid_strobe_i.value = 0

        # wait for the falling cs line
        await FallingEdge(dut.spi_cs_o)
        # check the serial data transmission
        sample_str = unsigned2bin(n, 8)
        for i in range(8):
            # check if the cs line does stay in the low state
            t1 = RisingEdge(dut.spi_clk_o)
            t2 = RisingEdge(dut.spi_cs_o)
            t_ret = await First(t1, t2)
            if t_ret is t2:
                assert False
            # check the current serial output
            assert dut.spi_mosi_o == sample_str[i]
            assert dut.spi_cs_o == 0

        # wait for the rising cs line to indicate the end of the transmission
        await RisingEdge(dut.spi_cs_o)
        await ClockCycles(dut.clk_i, 8)

    dut._log.info('Test finished')


