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

# import 
import numpy as np

def quantize_value(x, lsb):
    """This function quantize the given number so that it lies between -1 and 1-LSB. 
    Where LSB is the least significant bit of the bit vector   

    Args:
        x (float): number to quantize 
        lsb (float): value of the lsb

    Returns:
        float: quantize value
    """
    # no negative lsb values are allowed
    lsb = np.abs(lsb)

    # calculate the upper and lower bound for the quantize value
    upper_bound = 1 - lsb
    lower_bound = -1

    # we use truncation to quantize the value
    x_q = np.floor(x / lsb) * lsb

    # If the number does not lie within the limits, it is reshaped so that it lies within the limits. 
    # The wrap mode is used for this
    if x_q < lower_bound:
        x_q = x_q - 2 * lower_bound
    elif x_q > upper_bound:
        x_q = x_q + 2 * lower_bound

    return x_q


def square_puls(sfixed_fract, phase, threshold, n_samples):
    """The function generates a square puls according to a given phase and threshold.

    Args:
        sfixed_fract (int): sets the number of fractional bits
        phase (float): value that is accumulated per iteration
        threshold (float): threshold for the decision if the output is -1+LSB or 1-LSB
        n_samples (int): number of samples to generate

    Returns:
        np.array: array with all calculated square puls values
    """
    # storage for the output values
    calc_values = np.zeros(n_samples)
    # calc the lsb value for the quantization
    lsb = 2**(-sfixed_fract)
    # init the counter
    counter = 0

    # create the samples
    for i in range(0, n_samples):
        # perform the addition with overflow
        counter = quantize_value(counter + phase , lsb)
        # decision if the output is -1+LSB or 1-LSB
        if counter >= threshold:
            calc_values[i] = quantize_value(1-lsb, lsb)
        else:
            calc_values[i] = quantize_value(-1 + lsb, lsb)

    return calc_values