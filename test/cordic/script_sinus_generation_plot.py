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

# This script to generates a test plot of a generated sinus with a quantized python sinus generator

# import 
import numpy as np
import vp_sin_generator
import matplotlib.pyplot as plt

# configuration values for the sinus
Q7 = 7
PHASE = 0.308807373046875
#PHASE = 0.01
CORDIC_ITERATIONS = 6
NUMBER_OF_SAMPLES = 300

# create data of the sin
data = vp_sin_generator.sin_gen(Q7, PHASE, CORDIC_ITERATIONS, NUMBER_OF_SAMPLES)
x = np.arange(NUMBER_OF_SAMPLES)

# create figure of sin
plt.figure()
plt.title('Quantized Sinus generated with a cordic algorithm')
plt.xlabel('N')
plt.ylabel('y')
plt.plot(x, data)
plt.show()