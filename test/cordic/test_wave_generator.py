import cocotb
import numpy as np
import cordic
import sin_generator
from  bitstring import BitArray
from cocotb.triggers import Timer, FallingEdge, ClockCycles, RisingEdge, Join
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
async def cosim_wave_generator(dut):
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
    dut.enable_i.value = 0
    dut.set_phase_strobe_i.value = 0
    dut.set_amplitude_strobe_i.value = 0
    dut.waveform_i.value = unsigned2bin(0, 2) # set mode to sinus
    dut.data_i.value = frac2bin(0, sfixed_fract, FRAC_BITS)

    # start clock
    cocotb.start_soon(Clock(dut.clk_i, 10, units="ns").start())

    # reset dut
    await reset_dut(dut.rst_i, 20)

    # set amplitude and phase
    
    await RisingEdge(dut.clk_i)
    dut.data_i.value = frac2bin(phase, sfixed_fract, FRAC_BITS)
    dut.set_phase_strobe_i.value = 1

    await RisingEdge(dut.clk_i)
    dut.set_phase_strobe_i.value = 0

    await RisingEdge(dut.clk_i)
    dut.data_i.value = frac2bin(xi, sfixed_fract, FRAC_BITS)
    dut.set_amplitude_strobe_i.value = 1

    await RisingEdge(dut.clk_i)
    dut.set_amplitude_strobe_i.value = 0
    
    dut.enable_i.value = 1
    
    #ignore first out
    await RisingEdge(dut.data_valid_strobe_o)

    forked = cocotb.start_soon(check_value(dut, n_samples, calc_values, sfixed_fract, FRAC_BITS))
    await cocotb.start_soon(enable_control(dut))

    await Join(forked)

    dut._log.info('Test finished')

async def check_value(dut, n_samples, calc_values, sfixed_fract, FRAC_BITS):
    dut._log.info(f'#{0:>03} -> {"dut".center(8)} | {"python".center(8)}')
    for i in range(n_samples):

        await RisingEdge(dut.data_valid_strobe_o)
        
        dut._log.info(f'#{i:>03} -> {dut.data_o.value.binstr} | {frac2bin(calc_values[i], sfixed_fract, FRAC_BITS).binstr}')

        assert dut.data_o.value.binstr == frac2bin(calc_values[i], sfixed_fract, FRAC_BITS).binstr

async def enable_control(dut):
    await Timer(150, units='ns')
    dut.enable_i.value = 0
    await ClockCycles(dut.clk_i, 70)
    dut.enable_i.value = 1

    

