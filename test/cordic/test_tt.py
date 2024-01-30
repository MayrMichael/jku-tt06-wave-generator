import cocotb
import numpy as np
import cordic
import sin_generator
from  bitstring import BitArray
from cocotb.triggers import Timer, FallingEdge, ClockCycles, RisingEdge, Join, First
from cocotb.binary import BinaryValue, BinaryRepresentation 
from cocotb.clock import Clock

def frac2bin(x, sfixed_fract, frac_bits):
    return BinaryValue(value=BitArray(int=int(x * 2**sfixed_fract), length=frac_bits).bin, n_bits=frac_bits, binaryRepresentation=BinaryRepresentation.TWOS_COMPLEMENT )

def unsigned2bin(x, n_bits):
    return BinaryValue(value=BitArray(uint=x, length=n_bits).bin, n_bits=n_bits)

async def reset_dut(reset_n, duration_ns):
    reset_n.value = 0
    await Timer(duration_ns, units="ns")
    reset_n.value = 1
    reset_n._log.info("Reset complete")


@cocotb.test()
async def cosim_tt_sin(dut):
    iterations = 6
    sfixed_fract = 7
    phase = 0.308807373046875
    n_samples = 300

    FRAC_BITS = sfixed_fract + 1

    calc_values, xc_values, yc_values, zc_values, xi_values, yi_values, zi_values = sin_generator.sin_gen_debug(sfixed_fract, phase, iterations, n_samples)

    lsb = 2**(-sfixed_fract)
    shift_vector = cordic.gen_shift_vector(iterations)
    k = cordic.gen_k(shift_vector, lsb)

    xi = cordic.quantize_value(1.0 - lsb, lsb)
    xi = cordic.quantize_value(xi * k, lsb)
    xi = cordic.quantize_value(xi - lsb, lsb)

    # init values for dut
    dut.ena.value = 1
    dut.enable.value = 0
    dut.set_phase.value = 0
    dut.set_amplitude.value = 0
    dut.waveform.value = unsigned2bin(0, 2) # set mode to sinus
    dut.data_i.value = frac2bin(0, sfixed_fract, FRAC_BITS)

    # start clock
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())

    # reset dut
    await reset_dut(dut.rst_n, 20)

    # set amplitude and phase
    
    await RisingEdge(dut.clk)
    dut.data_i.value = frac2bin(phase, sfixed_fract, FRAC_BITS)
    dut.set_phase.value = 1

    await RisingEdge(dut.clk)
    dut.set_phase.value = 0

    await RisingEdge(dut.clk)
    dut.data_i.value = frac2bin(xi, sfixed_fract, FRAC_BITS)
    dut.set_amplitude.value = 1

    await RisingEdge(dut.clk)
    dut.set_amplitude.value = 0
    
    dut.enable.value = 1

    forked = cocotb.start_soon(check_value(dut, n_samples, calc_values, sfixed_fract, FRAC_BITS))
    await cocotb.start_soon(enable_control(dut))

    await Join(forked)

    dut._log.info('Test finished')

async def check_value(dut, n_samples, calc_values, sfixed_fract, FRAC_BITS):
    dut._log.info(f'#{0:>03} -> {"dut".center(8)} | {"python".center(8)}')
    for i in range(n_samples):

        await FallingEdge(dut.spi_cs)
        
        dut._log.info(f'#{i:>03} -> {dut.data_o.value.binstr} | {frac2bin(calc_values[i], sfixed_fract, FRAC_BITS).binstr}')

        assert dut.data_o.value.binstr == frac2bin(calc_values[i], sfixed_fract, FRAC_BITS).binstr

        sample_str = frac2bin(calc_values[i], sfixed_fract, FRAC_BITS)
        for k in range(8):
            t1 = RisingEdge(dut.spi_clk)
            t2 = RisingEdge(dut.spi_cs)
            t_ret = await First(t1, t2)
            if t_ret is t2:
                assert False
            dut._log.info(f'----- #{k:>03} -> {dut.spi_mosi.value.binstr}  | {sample_str[k].binstr}')
            assert dut.spi_mosi.value.binstr == sample_str[k].binstr
            assert dut.spi_cs.value == 0

        await RisingEdge(dut.spi_cs)

async def enable_control(dut):
    await Timer(2000, units='ns')
    dut.enable.value = 0
    await ClockCycles(dut.clk, 70)
    dut.enable.value = 1




