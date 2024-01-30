import numpy as np
import cordic
from bitstring import BitArray
from cocotb.binary import BinaryValue, BinaryRepresentation 

def frac2bin(x, sfixed_fract, frac_bits):
    return BinaryValue(value=BitArray(int=int(x * 2**sfixed_fract), length=frac_bits).bin, n_bits=frac_bits, binaryRepresentation=BinaryRepresentation.TWOS_COMPLEMENT )


sfixed_fract = 7
FRAC_BITS = sfixed_fract + 1



print(f'localparam HALF = {FRAC_BITS}\'b{frac2bin(0.5, sfixed_fract, FRAC_BITS).binstr};')
print(f'localparam MINUS_HALF = {FRAC_BITS}\'b{frac2bin(-0.5, sfixed_fract, FRAC_BITS).binstr};')
