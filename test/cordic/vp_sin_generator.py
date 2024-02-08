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

# imports
import numpy as np
import vp_cordic_iterative

def sin_gen(sfixed_fract, phase, iterations, n_samples):
    """The function generates a sinus according to a given phase. 
       The amplitude of the sinus is set as max value without an overflow

    Args:
        sfixed_fract (int): sets the number of fractional bits
        phase (float): phase difference between two samples of the sinus
        iterations (int): number of iterations for the cordic algorithm
        n_samples (int): number of samples to generate

    Returns:
        np.array: array with all calculated sinus values
    """
    calc_values, xc_values, yc_values, zc_values, xi_values, yi_values, zi_values = sin_gen_debug(sfixed_fract, phase, iterations, n_samples)
    return calc_values


def sin_gen_debug(sfixed_fract, phase, iterations, n_samples):
    """The function generates a sinus according to a given phase and returns additional values for debugging. 
       The amplitude of the sinus is set as max value without an overflow
       

    Args:
        sfixed_fract (int): sets the number of fractional bits
        phase (float): phase difference between two samples of the sinus
        iterations (int): number of iterations for the cordic algorithm
        n_samples (int): number of samples to generate

    Returns:
        (np.array, np.array, np.array, np.array, np.array, np.array, np.array): sinus values, x value after convergence, y value after convergence, 
                                                                                z value after convergence, x value before convergence, 
                                                                                y value before convergence, z value before convergence
    """
    # storage for the different values
    calc_values = np.zeros(n_samples)
    xc_values = np.zeros(n_samples)
    yc_values = np.zeros(n_samples)
    zc_values = np.zeros(n_samples)
    xi_values = np.zeros(n_samples)
    yi_values = np.zeros(n_samples)
    zi_values = np.zeros(n_samples)

    # calculate the needed values for the cordic algorithm
    lsb = 2**(-sfixed_fract)
    shift_vector = vp_cordic_iterative.gen_shift_vector(iterations)
    angles_vector = vp_cordic_iterative.gen_angles_vector(shift_vector, lsb)
    k = vp_cordic_iterative.gen_k(shift_vector, lsb)

    # calculate the maximum amplitude without overflow
    xi = vp_cordic_iterative.quantize_value(1.0 - lsb, lsb)
    xi = vp_cordic_iterative.quantize_value(xi * k, lsb)
    xi = vp_cordic_iterative.quantize_value(xi - lsb, lsb)

    # set the init values for y and z to get a sinus output
    yi = vp_cordic_iterative.quantize_value(0, lsb)
    zi = vp_cordic_iterative.quantize_value(0, lsb)

    # create the sinus samples
    for i in range(n_samples):
        # phase accumulator
        zi = vp_cordic_iterative.quantize_value(zi + phase, lsb)

        xc = xi
        yc = yi
        zc = zi

        # store the values before the convergence unit
        xi_values[i] = xc
        yi_values[i] = yc
        zi_values[i] = zc

        # convergence unit
        # this unit is responsible to keep the phase (zi) between -90° and 90°. 
        # If it is not between a rotation of +90° or -90° is performed. 
        if zi < -0.5:
            zc = zi + 0.5 
            xc = yi
            yc = -xi
        elif zi > 0.5:
            zc = zi - 0.5
            xc = -yi
            yc = xi

        # keep the values quantized
        xc = vp_cordic_iterative.quantize_value(xc, lsb)
        yc = vp_cordic_iterative.quantize_value(yc, lsb)
        zc = vp_cordic_iterative.quantize_value(zc, lsb)

        # store the values after the convergence unit
        xc_values[i] = xc
        yc_values[i] = yc
        zc_values[i] = zc

        # perform the cordic rotation
        xo, yo, zo = vp_cordic_iterative.cordic(xc,yc,zc, angles_vector, shift_vector, iterations, sfixed_fract)
        
        # store the sin values
        calc_values[i] = yo[iterations]

    return calc_values, xc_values, yc_values, zc_values, xi_values, yi_values, zi_values










