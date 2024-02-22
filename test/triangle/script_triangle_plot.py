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

# This script to generates a test plot of a generated triangle and sawtooth signal with a quantized python triangle generator

# import 
import numpy as np
import vp_triangle
import matplotlib.pyplot as plt

# configuration values
Q = 7
NUMBER_OF_SAMPLES = 300
PHASE = 0.01
AMP_LSB_MULTI = 40

# define amplitude with the lsb value
lsb = 2**(-Q)
amplitude = 1 - AMP_LSB_MULTI * lsb

# generate the sawtooth signal 
data_saw = vp_triangle.sawtooth(Q, PHASE, amplitude, NUMBER_OF_SAMPLES)
# generate the triangle signal
data_tri = vp_triangle.triangle(Q, PHASE, amplitude, NUMBER_OF_SAMPLES)

x = np.arange(NUMBER_OF_SAMPLES)

# create the figure of the square puls
plt.figure()
plt.title('Quantized triangle signal')
plt.xlabel('N')
plt.ylabel('y')
plt.plot(x, data_tri, label='triangle data')


plt.figure()
plt.title('Quantized sawtooth signal')
plt.xlabel('N')
plt.ylabel('y')
plt.plot(x, data_saw, label='sawtooth data')


plt.show()
