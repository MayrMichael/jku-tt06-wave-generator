import numpy as np
import cordic
from bitstring import BitArray
from cocotb.binary import BinaryValue, BinaryRepresentation 

def frac2bin(x, sfixed_fract, frac_bits):
    return BinaryValue(value=BitArray(int=int(x * 2**sfixed_fract), length=frac_bits).bin, n_bits=frac_bits, binaryRepresentation=BinaryRepresentation.TWOS_COMPLEMENT )

def unsigned2bin(x, n_bits):
    return BinaryValue(value=BitArray(uint=x, length=n_bits).bin, n_bits=n_bits)

def gen_verilog_shift_vector(iterations):
    return cordic.gen_shift_vector(iterations)

def gen_verilog_angle_vector(sfixed_fract, iterations):
    lsb = 2**(-sfixed_fract)
    shift_vector = cordic.gen_shift_vector(iterations)
    return cordic.gen_angles_vector(shift_vector, lsb)

iterations = 6
sfixed_fract = 7
FRAC_BITS = sfixed_fract + 1
BW_SHIFT_VALUE = 3

shift_vector = gen_verilog_shift_vector(iterations)

# sv_str = f'localparam [BW_SHIFT_VECTOR:0] SHIFT_VECTOR [0:{len(shift_vector)-1}] = '
# sv_str += '{'

# for i in range(len(shift_vector)):
#     sv_str += f'{BW_SHIFT_VALUE}\'b{unsigned2bin(shift_vector[i], BW_SHIFT_VALUE)}'
#     if i <  len(shift_vector) - 1:
#         sv_str += ', '

# sv_str += '};'

print(f'localparam ITERATIONS = {iterations};')
print(f'localparam BW_SHIFT_VECTOR = {BW_SHIFT_VALUE};')

print(f'wire [BW_SHIFT_VECTOR-1:0] SHIFT_VECTOR [0:{len(shift_vector)-1}];')
for i in range(len(shift_vector)):
    print(f'assign SHIFT_VECTOR[{i}] = {BW_SHIFT_VALUE}\'b{unsigned2bin(shift_vector[i], BW_SHIFT_VALUE)};')

# print(sv_str)

angles_vector = gen_verilog_angle_vector(sfixed_fract, iterations)

# av_str = f'localparam [{FRAC_BITS - 1}:0] ANGLES_VECTOR [0:{len(angles_vector)-1}] = '
# av_str += '{'

# for i in range(len(angles_vector)):
#     av_str += f'{FRAC_BITS}\'b{frac2bin(angles_vector[i], sfixed_fract, FRAC_BITS).binstr}'

#     if i <  len(angles_vector) - 1:
#         av_str += ', '

# av_str += '};'

# print(av_str)

print(f'wire [{FRAC_BITS - 1}:0] ANGLES_VECTOR [0:{len(angles_vector)-1}];')
for i in range(len(angles_vector)):
    print(f'assign ANGLES_VECTOR[{i}] = {FRAC_BITS}\'b{frac2bin(angles_vector[i], sfixed_fract, FRAC_BITS).binstr};')