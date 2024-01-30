import cocotb
import numpy as np
import triangle
import square_puls
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
async def cosim_tt_sawtooth(dut):

    sfixed_fract = 7
    phase = 0.01
    n_samples = 300

    FRAC_BITS = sfixed_fract + 1
    lsb = 2**(-sfixed_fract)
   
    amplitude = 1 - 40 * lsb

    phase = triangle.quantize_value(phase, lsb)
    amplitude = triangle.quantize_value(amplitude, lsb)

    calc_values = triangle.sawtooth(sfixed_fract, phase, amplitude, n_samples)

    # init values for dut
    dut.ena.value = 1
    dut.enable.value = 0
    dut.set_phase.value = 0
    dut.set_amplitude.value = 0
    dut.waveform.value = unsigned2bin(2, 2) # set mode to sawtooth
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
    dut.data_i.value = frac2bin(amplitude, sfixed_fract, FRAC_BITS)
    dut.set_amplitude.value = 1

    await RisingEdge(dut.clk)
    dut.set_amplitude.value = 0
    
    dut.enable.value = 1

    forked = cocotb.start_soon(check_value(dut, n_samples, calc_values, sfixed_fract, FRAC_BITS))
    await cocotb.start_soon(enable_control(dut))

    await Join(forked)

    dut._log.info('Test finished')


@cocotb.test()
async def cosim_tt_triangle(dut):

    sfixed_fract = 7
    phase = 0.01
    n_samples = 300

    FRAC_BITS = sfixed_fract + 1
    lsb = 2**(-sfixed_fract)
   
    amplitude = 1 - 40 * lsb

    phase = triangle.quantize_value(phase, lsb)
    amplitude = triangle.quantize_value(amplitude, lsb)

    calc_values = triangle.triangle(sfixed_fract, phase, amplitude, n_samples)

    # init values for dut
    dut.ena.value = 1
    dut.enable.value = 0
    dut.set_phase.value = 0
    dut.set_amplitude.value = 0
    dut.waveform.value = unsigned2bin(3, 2) # set mode to triangle
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
    dut.data_i.value = frac2bin(amplitude, sfixed_fract, FRAC_BITS)
    dut.set_amplitude.value = 1

    await RisingEdge(dut.clk)
    dut.set_amplitude.value = 0
    
    dut.enable.value = 1

    forked = cocotb.start_soon(check_value(dut, n_samples, calc_values, sfixed_fract, FRAC_BITS))
    await cocotb.start_soon(enable_control(dut))

    await Join(forked)

    dut._log.info('Test finished')


@cocotb.test()
async def cosim_tt_square_puls(dut):

    sfixed_fract = 7
    phase = 0.01
    threshold = 0.2
    n_samples = 300

    FRAC_BITS = sfixed_fract + 1
    lsb = 2**(-sfixed_fract)
   

    phase = square_puls.quantize_value(phase, lsb)
    threshold = square_puls.quantize_value(threshold, lsb)

    calc_values = square_puls.square_puls(sfixed_fract, phase, threshold, n_samples)

    # init values for dut
    dut.ena.value = 1
    dut.enable.value = 0
    dut.set_phase.value = 0
    dut.set_amplitude.value = 0
    dut.waveform.value = unsigned2bin(1, 2) # set mode to square pulse
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
    dut.data_i.value = frac2bin(threshold, sfixed_fract, FRAC_BITS)
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


def create_vars_sawtooth():
    sfixed_fract = 7
    phase = 0.01
    threshold = 0.2
    n_samples = 300

    FRAC_BITS = sfixed_fract + 1
    lsb = 2**(-sfixed_fract)
   

    phase = square_puls.quantize_value(phase, lsb)
    threshold = square_puls.quantize_value(threshold, lsb)

    calc_values = square_puls.square_puls(sfixed_fract, phase, threshold, n_samples)


    # init values for dut
    print(f'dut.waveform.value = {unsigned2bin(1, 2).binstr}')
    print(f'dut.data_i.value = {frac2bin(0, sfixed_fract, FRAC_BITS).binstr}')




    # set amplitude and phase
    

    print(f'data_i.value = {frac2bin(phase, sfixed_fract, FRAC_BITS).binstr}')

    print(f'dut.data_i.value = {frac2bin(threshold, sfixed_fract, FRAC_BITS).binstr}')

    lstr = []
    for i in range(n_samples):
        lstr.append(frac2bin(calc_values[i], sfixed_fract, FRAC_BITS).binstr)
    strs = '\', \''.join(lstr)
    print(f'[{strs}]')


if __name__ == '__main__':
    create_vars_sawtooth()