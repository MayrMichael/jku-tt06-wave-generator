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

# This script to generates a test plot of a generated square puls sequence with a quantized python square puls generator

# import 
import numpy as np
import vp_square_puls
import matplotlib.pyplot as plt

# configuration values
Q = 7
NUMBER_OF_SAMPLES = 300
PHASE = 0.01
THRESHOLD = 0.2

# create the data of the square puls sequence
data_sq = vp_square_puls.square_puls(Q, PHASE, THRESHOLD, NUMBER_OF_SAMPLES)

x = np.arange(NUMBER_OF_SAMPLES)

# create the figure of the square puls
plt.figure()
plt.title('Quantized square puls signal')
plt.xlabel('N')
plt.ylabel('y')
plt.plot(x, data_sq)
plt.show()