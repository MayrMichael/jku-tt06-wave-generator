import cocotb
import numpy as np
import cordic
import sin_generator
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
async def cosim_sin_generator(dut):
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

    dut.next_data_strobe_i.value = 0

    dut.phase_i.value = frac2bin(phase, sfixed_fract, FRAC_BITS)
    dut.amplitude_i.value = frac2bin(xi, sfixed_fract, FRAC_BITS)

    cocotb.start_soon(Clock(dut.clk_i, 10, units="ns").start())

    # reset dut
    await reset_dut(dut.rst_i, 20)

    # set amplitude and phase
    await FallingEdge(dut.clk_i)

    dut._log.info(f'#{0:>03} -> {"dut".center(8)} | {"python".center(8)}')
    for i in range(n_samples):
        await FallingEdge(dut.clk_i)
        dut.next_data_strobe_i.value = 1

        await RisingEdge(dut.phase_increment_done_strobe)
        dut.next_data_strobe_i.value = 0

        # dut._log.info('----------------------- input convergence ----------------------------------')
        # dut._log.info(f'{dut.amplitude.value.binstr} | {dut.y_const.value.binstr} | {dut.z_phase.value.binstr} | dut')
        # dut._log.info(f'{frac2bin(xi_values[i], sfixed_fract, FRAC_BITS).binstr} | {frac2bin(yi_values[i], sfixed_fract, FRAC_BITS).binstr} | {frac2bin(zi_values[i], sfixed_fract, FRAC_BITS).binstr} | python')
        assert dut.amplitude_i.value.binstr == frac2bin(xi_values[i], sfixed_fract, FRAC_BITS).binstr
        assert dut.y_const.value.binstr == frac2bin(yi_values[i], sfixed_fract, FRAC_BITS).binstr
        assert dut.z_phase.value.binstr == frac2bin(zi_values[i], sfixed_fract, FRAC_BITS).binstr
        # dut._log.info('-------------------------------------------------------------------------------')

        await RisingEdge(dut.data_con_out_valid_strobe)
        # dut._log.info('----------------------- output convergence ----------------------------------')
        # dut._log.info(f'{dut.x_con_out.value.binstr} | {dut.y_con_out.value.binstr} | {dut.z_con_out.value.binstr} | dut')
        # dut._log.info(f'{frac2bin(xc_values[i], sfixed_fract, FRAC_BITS).binstr} | {frac2bin(yc_values[i], sfixed_fract, FRAC_BITS).binstr} | {frac2bin(zc_values[i], sfixed_fract, FRAC_BITS).binstr} | python')
        assert dut.x_con_out.value.binstr == frac2bin(xc_values[i], sfixed_fract, FRAC_BITS).binstr
        assert dut.y_con_out.value.binstr == frac2bin(yc_values[i], sfixed_fract, FRAC_BITS).binstr
        assert dut.z_con_out.value.binstr == frac2bin(zc_values[i], sfixed_fract, FRAC_BITS).binstr
        # dut._log.info('-------------------------------------------------------------------------------')


        await RisingEdge(dut.data_out_valid_strobe_o)
        await Timer(10, units='ps')

        # dut._log.info(f'#{i:>03} {dut.x_con_out.value.binstr}, {dut.y_con_out.value.binstr}, {dut.z_con_out.value.binstr} -> {dut.y_cordic_out.value.binstr} | {frac2bin(calc_values[i], sfixed_fract, FRAC_BITS).binstr} | {dut.y_cordic_out.value.binstr == frac2bin(calc_values[i], sfixed_fract, FRAC_BITS).binstr}')
        
        dut._log.info(f'#{i:>03} -> {dut.data_o.value.binstr} | {frac2bin(calc_values[i], sfixed_fract, FRAC_BITS).binstr}')

        assert dut.data_o.value.binstr == frac2bin(calc_values[i], sfixed_fract, FRAC_BITS).binstr
   
    
    dut._log.info('Test finished')
    

