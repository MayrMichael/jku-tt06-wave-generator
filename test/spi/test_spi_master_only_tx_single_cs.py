import cocotb
from bitstring import BitArray
from cocotb.triggers import Timer, FallingEdge, ClockCycles, RisingEdge, Join, First
from cocotb.binary import BinaryValue, BinaryRepresentation 
from cocotb.clock import Clock

def unsigned2bin(x, n_bits):
    return BinaryValue(value=BitArray(uint=x, length=n_bits).bin, n_bits=n_bits)

async def reset_dut(reset_n, duration_ns):
    reset_n.value = 0
    await Timer(duration_ns, units="ns")
    reset_n.value = 1
    reset_n._log.info("Reset complete")

@cocotb.test()
async def test_spi_master(dut):
    n_samples = 16
    
    samples = list(range(n_samples))
    samples.extend([128, 255, 128, 255, 0])
    
    dut.data_in_valid_strobe_i.value = 0
    dut.data_i.value = unsigned2bin(0, 8)

    cocotb.start_soon(Clock(dut.clk_i, 10, units="ns").start())

    # reset dut
    await reset_dut(dut.rst_i, 20)

    await ClockCycles(dut.clk_i, 1)

    for i, n in enumerate(samples):
        dut.data_in_valid_strobe_i.value = 1
        dut.data_i.value = unsigned2bin(n, 8)
        await ClockCycles(dut.clk_i, 1)
        dut.data_in_valid_strobe_i.value = 0
        await FallingEdge(dut.spi_cs_o)
        forked = cocotb.start_soon(check_value(dut, n))

        await Join(forked)
        await RisingEdge(dut.spi_cs_o)
        await ClockCycles(dut.clk_i, 8)

        
    
    dut._log.info('Test finished')


async def check_value(dut, sample):
    sample_str = unsigned2bin(sample, 8)
    for i in range(8):
        t1 = RisingEdge(dut.spi_clk_o)
        t2 = RisingEdge(dut.spi_cs_o)
        t_ret = await First(t1, t2)
        if t_ret is t2:
            assert False
        assert dut.spi_mosi_o == sample_str[i]
        assert dut.spi_cs_o == 0

