import cocotb
import numpy as np
import triangle
import square_puls
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
async def cosim_wave_generator_sawtooth(dut):

    sfixed_fract = 7
    phase = 0.01
    n_samples = 1000

    FRAC_BITS = sfixed_fract + 1
    lsb = 2**(-sfixed_fract)

    amplitude = 1 - 40 * lsb

    phase = triangle.quantize_value(phase, lsb)
    amplitude = triangle.quantize_value(amplitude, lsb)

    calc_values = triangle.sawtooth(sfixed_fract, phase, amplitude, n_samples)

    # init values for dut
    dut.enable_i.value = 0
    dut.set_phase_strobe_i.value = 0
    dut.set_amplitude_strobe_i.value = 0
    dut.waveform_i.value = unsigned2bin(2, 2) # set mode to sawtooth
    dut.data_i.value = frac2bin(0, sfixed_fract, FRAC_BITS)

    # start clock
    cocotb.start_soon(Clock(dut.clk_i, 10, units="ns").start())

    # reset dut
    await reset_dut(dut.rst_i, 20)

    # set amplitude (threshold) and phase

    await RisingEdge(dut.clk_i)
    dut.data_i.value = frac2bin(phase, sfixed_fract, FRAC_BITS)
    dut.set_phase_strobe_i.value = 1

    await RisingEdge(dut.clk_i)
    dut.set_phase_strobe_i.value = 0

    await RisingEdge(dut.clk_i)
    dut.data_i.value = frac2bin(amplitude, sfixed_fract, FRAC_BITS)
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

@cocotb.test()
async def cosim_wave_generator_triangle(dut):

    sfixed_fract = 7
    phase = 0.01
    n_samples = 1000

    FRAC_BITS = sfixed_fract + 1
    lsb = 2**(-sfixed_fract)

    amplitude = 1 - 40 * lsb

    phase = triangle.quantize_value(phase, lsb)
    amplitude = triangle.quantize_value(amplitude, lsb)

    calc_values = triangle.triangle(sfixed_fract, phase, amplitude, n_samples)

    # init values for dut
    dut.enable_i.value = 0
    dut.set_phase_strobe_i.value = 0
    dut.set_amplitude_strobe_i.value = 0
    dut.waveform_i.value = unsigned2bin(3, 2) # set mode to triangle
    dut.data_i.value = frac2bin(0, sfixed_fract, FRAC_BITS)

    # start clock
    cocotb.start_soon(Clock(dut.clk_i, 10, units="ns").start())

    # reset dut
    await reset_dut(dut.rst_i, 20)

    # set amplitude (threshold) and phase

    await RisingEdge(dut.clk_i)
    dut.data_i.value = frac2bin(phase, sfixed_fract, FRAC_BITS)
    dut.set_phase_strobe_i.value = 1

    await RisingEdge(dut.clk_i)
    dut.set_phase_strobe_i.value = 0

    await RisingEdge(dut.clk_i)
    dut.data_i.value = frac2bin(amplitude, sfixed_fract, FRAC_BITS)
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

@cocotb.test()
async def cosim_square_puls(dut):

    sfixed_fract = 7
    phase = 0.1
    threshold = 0.2
    n_samples = 1000

    FRAC_BITS = sfixed_fract + 1
    lsb = 2**(-sfixed_fract)

    phase = square_puls.quantize_value(phase, lsb)
    threshold = square_puls.quantize_value(threshold, lsb)

    calc_values = square_puls.square_puls(sfixed_fract, phase, threshold, n_samples)

    # init values for dut
    dut.enable_i.value = 0
    dut.set_phase_strobe_i.value = 0
    dut.set_amplitude_strobe_i.value = 0
    dut.waveform_i.value = unsigned2bin(1, 2) # set mode to square pulse
    dut.data_i.value = frac2bin(0, sfixed_fract, FRAC_BITS)

    # start clock
    cocotb.start_soon(Clock(dut.clk_i, 10, units="ns").start())

    # reset dut
    await reset_dut(dut.rst_i, 20)

    # set amplitude (threshold) and phase

    await RisingEdge(dut.clk_i)
    dut.data_i.value = frac2bin(phase, sfixed_fract, FRAC_BITS)
    dut.set_phase_strobe_i.value = 1

    await RisingEdge(dut.clk_i)
    dut.set_phase_strobe_i.value = 0

    await RisingEdge(dut.clk_i)
    dut.data_i.value = frac2bin(threshold, sfixed_fract, FRAC_BITS)
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
    