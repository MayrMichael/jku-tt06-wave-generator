import cocotb
from bitstring import BitArray
from cocotb.triggers import Timer, FallingEdge, ClockCycles, RisingEdge
from cocotb.binary import BinaryValue, BinaryRepresentation 
from cocotb.clock import Clock

async def reset_dut(reset_n, duration_ns):
    reset_n.value = 0
    await Timer(duration_ns, units="ns")
    reset_n.value = 1
    reset_n._log.info("Reset complete")

@cocotb.test()
async def test_strobe_generator(dut):
    n_strobes = 4
    
    dut.enable_i.value = 0


    cocotb.start_soon(Clock(dut.clk_i, 10, units="ns").start())

    # reset dut
    await reset_dut(dut.rst_i, 20)

    await ClockCycles(dut.clk_i, 1)
    dut.enable_i.value = 1

    for i in range(n_strobes):
        await RisingEdge(dut.strobe_o)
    
    dut._log.info('Test finished')