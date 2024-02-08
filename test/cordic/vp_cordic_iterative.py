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

# converts the function into a function, that can work with numpy arrays
quantize_value_vec = np.vectorize(quantize_value)

def sra(x, s, sfixed_fract):
    """Function that performs a shift right arithmetic on a quantize value

    Args:
        x (float): value to be shifted
        s (int): sets the number of shifts
        sfixed_fract (int): sets the number of fractional bits

    Returns:
        float: shifted value
    """

    if s == 0:
        return x # if shift is equal to zero we keep the value
    else:
        # we perform the shift operation in the integer range.
        # Therefore we assume the value is quantized with the given fractional bits
        x_int = int(x * 2**sfixed_fract)
        # perform the shift
        x_int = x_int >> s
        # convert the integer back to a float number that lies in the borders of the 
        # given fractional bits
        return x_int / 2**sfixed_fract

        
def cordic(xi, yi, zi, angles_vector, shift_vector, iterations, sfixed_fract):
    """This function performs the cordic algorithm. However, with the restriction that 
    the algorithm only supports the rotation mode and as coordinate system only the circular system. 

    Args:
        xi (float): x input value (should be scaled with the k value)
        yi (float): y input value (should be scaled with the k value)
        zi (float): z input value (must lie between -100° and 100°)
        angles_vector (np.array): micro angeles for the iterations
        shift_vector (np.array): shift values per iteration
        iterations (int): amount of iterations
        sfixed_fract (int): sets the number of fractional bits

    Returns:
        (np.array, np.array, np.array): returns a tuple (x,y,z) with all intermediate results and 
                                        the final result of the algorithm
    """
    # calculate the lsb value for the given fraction bits
    lsb = 2**(-sfixed_fract)

    # create the storage for the values
    xo = np.zeros(iterations+1)
    yo = np.zeros(iterations+1)
    zo = np.zeros(iterations+1)

    # initialize the cordic algorithm
    xo[0] = xi
    yo[0] = yi
    zo[0] = zi

    for i in range(iterations):
        # define to rotation direction of the iteration
        # if sigma is 1 we add the micro angle else we subtract it 
        # sigma is depending on the last zo
        sigma = -1
        if zo[i] >= 0:
            sigma = 1

        # perform the shifts
        y_shift = quantize_value(sra(yo[i], shift_vector[i], sfixed_fract), lsb)
        x_shift = quantize_value(sra(xo[i], shift_vector[i], sfixed_fract), lsb)

        # calculate the next values for the cordic iterations
        xo[i+1] = quantize_value(xo[i] - sigma * y_shift, lsb)
        yo[i+1] = quantize_value(yo[i] + sigma * x_shift, lsb)
        zo[i+1] = quantize_value(zo[i] - sigma * angles_vector[i], lsb)

    return xo, yo, zo

def gen_shift_vector(n):
    """creates a array with all shift values for the cordic algorithm (only rotation, only circular coordinate system)

    Args:
        n (int): number of cordic iterations

    Returns:
        np.array: shift values
    """
    return np.arange(n)

def gen_k(shift_vector, lsb):
    """creates the value for scaling of the inputs x and y of the cordic algorithm. This Value compensate the length error because of the algorithm.

    Args:
        shift_vector (np.array): array with all shift values
        lsb (float): least significant bit of the fractional bits

    Returns:
        float: k value for scaling
    """
    return quantize_value(np.prod(1 / np.sqrt(1 + np.power(2 * np.ones(len(shift_vector)),(-2 * shift_vector)))),lsb)

def gen_angles_vector(shift_vector, lsb):
    """creates the micro angeles array for the cordic algorithm (only rotation, only circular coordinate system)

    Args:
        shift_vector (np.array): array with all shift values
        lsb (float): least significant bit of the fractional bits

    Returns:
        np.array: array with all micro angeles
    """
    angles_vector = np.arctan(np.power(2 * np.ones(len(shift_vector)),(-shift_vector))) / np.pi
    return quantize_value_vec(angles_vector, lsb)

def get_rotated_vector(phase, sfixed_fract, iterations):
    """This function performs a rotation according to a phase value with a maximum amplitude that doesn't overflow. 
       The starting point is defined as: x is set to the max amplitude and y is set to zero.

    Args:
        phase (float): phase value to rotate
        sfixed_fract (int): sets the number of fractional bits
        iterations (int): number of iterations for the cordic algorithm

    Returns:
        np.array, np.array: sine value, cosine value for the given phase
    """
    # generate the values for the cordic according to the iteration value and the number of fractional bits
    lsb = 2**(-sfixed_fract)
    shift_vector = gen_shift_vector(iterations)
    angles_vector = gen_angles_vector(shift_vector, lsb)
    k = gen_k(shift_vector, lsb)

    # calculate the max amplitude that doesn't overflow
    xi = quantize_value(1.0 - lsb, lsb)
    xi = quantize_value(xi * k, lsb)
    yi = quantize_value(0, lsb)
    zi = quantize_value(phase, lsb)

    # perform the cordic algorithm
    xo, yo, zo = cordic(xi,yi,zi, angles_vector, shift_vector, iterations, sfixed_fract)

    return xo[iterations], yo[iterations]















