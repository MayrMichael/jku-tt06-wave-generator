# Copyright 2024 Michael Mayr
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE−2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# This script to compare various configurations of the cordic algorithm

# imports
import numpy as np
import matplotlib.pyplot as plt
import vp_cordic_iterative

# phase for the comparison of the q formats and iterations
PHASE = 0.308807373046875

# different cordic configurations for comparing
result_xy_15_15 = vp_cordic_iterative.get_rotated_vector(PHASE, sfixed_fract=15, iterations=15)
result_xy_7_8 = vp_cordic_iterative.get_rotated_vector(PHASE, sfixed_fract=7, iterations=8)
result_xy_7_6 = vp_cordic_iterative.get_rotated_vector(PHASE, sfixed_fract=7, iterations=6)

# double floating point result
result_xy_np =  (np.cos(PHASE * np.pi), np.sin(PHASE * np.pi))

# the parallel output has 8 bits therefore we look at Q7 quantized values for comparison
lsb = 2**(-7)
result_quantized_xy_15_15 = vp_cordic_iterative.quantize_value_vec(result_xy_15_15, lsb)
result_quantized_xy_7_8 = vp_cordic_iterative.quantize_value_vec(result_xy_7_8, lsb)
result_quantized_xy_7_6 = vp_cordic_iterative.quantize_value_vec(result_xy_7_6, lsb)
result_quantized_xy_np = vp_cordic_iterative.quantize_value_vec(result_xy_np, lsb)

# create plot
plt.figure()
plt.title('Cordic algorithm with different Q numbers \n and iterations quantized to Q7')
plt.plot([0, result_quantized_xy_15_15[0]], [0, result_quantized_xy_15_15[1]], 'o--', label='quantized Q15 with 15 iterations')
plt.plot([0, result_quantized_xy_7_8[0]], [0, result_quantized_xy_7_8[1]], 'o--', label='quantized Q7 with 8 iterations')
plt.plot([0, result_quantized_xy_7_6[0]], [0, result_quantized_xy_7_6[1]], 'o--', label='quantized Q7 with 6 iterations')
plt.plot([0, result_quantized_xy_np[0]], [0, result_quantized_xy_np[1]], 'o--', label='quantized double floating point')
plt.xlabel('x')
plt.ylabel('y')
plt.legend()
plt.grid()
plt.show()





#plt.plot(0,0,'ok') #<-- plot a black point at the origin
# 
# plt.xlim([-1.2,1.2]) #<-- set the x axis limits
# plt.ylim([-1.2,1.2]) #<-- set the y axis limits
# plt.legend( ['original','original quant 8 Bit', '8 Bits, 8 Iterations', '8 Bits, 6 Iterations','16 Bits, 15 Iterations']) #<-- give a legend
# plt.grid() #<-- plot grid lines
# plt.show()