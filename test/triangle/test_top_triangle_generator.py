import cocotb
import numpy as np
import triangle
import square_puls
from  bitstring import BitArray
from cocotb.triggers import Timer, FallingEdge, ClockCycles, RisingEdge
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
async def cosim_sawtooth_generator(dut):

    sfixed_fract = 7
    
    phase = 0.01
    n_samples = 1000

    FRAC_BITS = sfixed_fract + 1
    lsb = 2**(-sfixed_fract)

    amplitude = 1 - 40 * lsb

    phase = triangle.quantize_value(phase, lsb)
    amplitude = triangle.quantize_value(amplitude, lsb)

    calc_values = triangle.sawtooth(sfixed_fract, phase, amplitude, n_samples)

    dut.overflow_mode_i.value = 0
    dut.next_data_strobe_i.value = 0
    dut.phase_i.value = frac2bin(phase, sfixed_fract, FRAC_BITS)
    dut.amplitude_i.value = frac2bin(amplitude, sfixed_fract, FRAC_BITS)

    cocotb.start_soon(Clock(dut.clk_i, 10, units="ns").start())

    # reset dut
    await reset_dut(dut.rst_i, 20)


    dut._log.info(f'#{0:>03} -> {"dut".center(8)} | {"python".center(8)}')
    for i in range(n_samples):
        await FallingEdge(dut.clk_i)
        dut.next_data_strobe_i.value = 1

        await RisingEdge(dut.data_sawtooth_out_valid_strobe_o)
        dut.next_data_strobe_i.value = 0

        if dut.data_sawtooth_o.value.binstr != frac2bin(calc_values[i], sfixed_fract, FRAC_BITS).binstr:
            dut._log.info(f'#{i:>03} -> {dut.data_sawtooth_o.value.binstr} | {frac2bin(calc_values[i], sfixed_fract, FRAC_BITS).binstr}')

        assert dut.data_sawtooth_o.value.binstr == frac2bin(calc_values[i], sfixed_fract, FRAC_BITS).binstr

        await FallingEdge(dut.clk_i)
    
    dut._log.info('Test finished')
    

@cocotb.test()
async def cosim_triangle_generator(dut):

    sfixed_fract = 7
    
    phase = 0.01
    n_samples = 1000

    FRAC_BITS = sfixed_fract + 1
    lsb = 2**(-sfixed_fract)

    amplitude = 1 - 40 * lsb

    phase = triangle.quantize_value(phase, lsb)
    amplitude = triangle.quantize_value(amplitude, lsb)

    calc_values = triangle.triangle(sfixed_fract, phase, amplitude, n_samples)

    dut.overflow_mode_i.value = 0
    dut.next_data_strobe_i.value = 0
    dut.phase_i.value = frac2bin(phase, sfixed_fract, FRAC_BITS)
    dut.amplitude_i.value = frac2bin(amplitude, sfixed_fract, FRAC_BITS)

    cocotb.start_soon(Clock(dut.clk_i, 10, units="ns").start())

    # reset dut
    await reset_dut(dut.rst_i, 20)


    dut._log.info(f'#{0:>03} -> {"dut".center(8)} | {"python".center(8)}')
    for i in range(n_samples):
        await FallingEdge(dut.clk_i)
        dut.next_data_strobe_i.value = 1

        await FallingEdge(dut.clk_i)
        dut.next_data_strobe_i.value = 0


        await RisingEdge(dut.data_triangle_out_valid_strobe_o)

        if dut.data_triangle_o.value.binstr != frac2bin(calc_values[i], sfixed_fract, FRAC_BITS).binstr:
            dut._log.info(f'#{i:>03} -> {dut.data_triangle_o.value.binstr} | {frac2bin(calc_values[i], sfixed_fract, FRAC_BITS).binstr}')

        assert dut.data_triangle_o.value.binstr == frac2bin(calc_values[i], sfixed_fract, FRAC_BITS).binstr
   
    
    dut._log.info('Test finished')


@cocotb.test()
async def cosim_square_puls(dut):

    sfixed_fract = 7
    phase = 0.1
    threshold = 0.1
    n_samples = 1000

    FRAC_BITS = sfixed_fract + 1
    lsb = 2**(-sfixed_fract)

    phase = square_puls.quantize_value(phase, lsb)
    threshold = square_puls.quantize_value(threshold, lsb)

    calc_values = square_puls.square_puls(sfixed_fract, phase, threshold, n_samples)

    dut.overflow_mode_i.value = 1
    dut.next_data_strobe_i.value = 0
    dut.phase_i.value = frac2bin(phase, sfixed_fract, FRAC_BITS)
    dut.amplitude_i.value = frac2bin(threshold, sfixed_fract, FRAC_BITS)

    cocotb.start_soon(Clock(dut.clk_i, 10, units="ns").start())

    # reset dut
    await reset_dut(dut.rst_i, 20)


    dut._log.info(f'#{0:>03} -> {"dut".center(8)} | {"python".center(8)}')
    for i in range(n_samples):
        await FallingEdge(dut.clk_i)
        dut.next_data_strobe_i.value = 1

        await FallingEdge(dut.clk_i)
        dut.next_data_strobe_i.value = 0


        await RisingEdge(dut.data_square_puls_out_valid_strobe_o)
        
        if dut.data_square_puls_o.value.binstr != frac2bin(calc_values[i], sfixed_fract, FRAC_BITS).binstr:
            dut._log.info(f'#{i:>03} -> {dut.data_square_puls_o.value.binstr} | {frac2bin(calc_values[i], sfixed_fract, FRAC_BITS).binstr}')

        assert dut.data_square_puls_o.value.binstr == frac2bin(calc_values[i], sfixed_fract, FRAC_BITS).binstr
   
    
    dut._log.info('Test finished')