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


def counter(sfixed_fract, phase, amplitude, n_samples):
    lsb = 2**(-sfixed_fract)

    calc_values = np.zeros(n_samples)
    counter = quantize_value(phase, lsb)
    calc_values[0] = counter

    for i in range(1, n_samples):
        if counter <= amplitude:
            counter = quantize_value(counter + phase , lsb)
        else:
            counter = quantize_value(counter * (-1), lsb)
        calc_values[i] = counter

    return calc_values

def sawtooth(sfixed_fract, phase, amplitude, n_samples):
    """The function generates a sawtooth signal according to a given phase and amplitude.

    Args:
        sfixed_fract (int): sets the number of fractional bits
        phase (float): value that is accumulated per iteration
        amplitude (float): amplitude value of the signal. The signal lies in [-amplitude, amplitude]
        n_samples (int): number of samples to generate

    Returns:
        np.array: array with all calculated sawtooth values
    """
    # storage for the output values
    calc_values = np.zeros(n_samples)
    # init value for the counter
    lsb = 2**(-sfixed_fract)
    counter = quantize_value(phase, lsb)
    calc_values[0] = counter
    
    # create the samples
    for i in range(1, n_samples):
        # check the current counter value if it lies in +/- amplitude. If not negate.
        if counter <= amplitude:
            counter = quantize_value(counter + phase , lsb)
        else:
            counter = quantize_value(counter * (-1), lsb)
        
        calc_values[i] = counter

    return calc_values

def triangle(sfixed_fract, phase, amplitude, n_samples):
    """The function generates a triangle signal according to a given phase and amplitude.

    Args:
        sfixed_fract (int): sets the number of fractional bits
        phase (float): value that is accumulated per iteration
        amplitude (float): amplitude value of the signal. The signal lies in [-amplitude, amplitude]
        n_samples (int): number of samples to generate

    Returns:
        np.array: array with all calculated triangle values
    """
    # storage for the output values
    calc_values = np.zeros(n_samples)
    
    # init value for the counter
    lsb = 2**(-sfixed_fract)
    counter = quantize_value(phase, lsb)
    calc_values[0] = counter
    old_counter = counter

    # define additional status bits for detecting and executing the reverse operation of the counter values 
    reverse = False
    rev_counter = 0

    # create the samples
    for i in range(1, n_samples):
        # check the current counter value if it lies in +/- amplitude. If not negate.
        if counter <= amplitude:
            counter = quantize_value(counter + phase , lsb)
        else:
            counter = quantize_value(counter * (-1), lsb)

        inter_counter = counter

        # check whether an overflow has occurred or not
        if np.signbit(counter) != np.signbit(old_counter):
            # ignore always one overflow
            if rev_counter == 0:
                # change the reverse bit
                reverse = not reverse
                rev_counter = 1
            else:
                rev_counter = 0

        # to generate the falling ramp negate the rising ramp in the right state
        if reverse:
            calc_values[i] = quantize_value(inter_counter * (-1), lsb)
        else:
            calc_values[i] = quantize_value(inter_counter, lsb)

        # save the old value for the overflow detection
        old_counter = counter

    return calc_values
