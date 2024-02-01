import numpy as np

def quantize_value(x, lsb):
    lsb = np.abs(lsb)

    upper_bound = 1 - lsb
    lower_bound = -1

    x_q = np.floor(x / lsb) * lsb

    if x_q < lower_bound:
        x_q = x_q - 2 * lower_bound
    elif x_q > upper_bound:
        x_q = x_q + 2 * lower_bound

    return x_q

quantize_value_vec = np.vectorize(quantize_value)

def sra(x, s, sfixed_fract):
    if s == 0:
        return x
    else:
        x_int = int(x * 2**sfixed_fract)
        x_int = x_int >> s
        return x_int / 2**sfixed_fract

        
def cordic(xi, yi, zi, angles_vector, shift_vector, iterations, sfixed_fract):
    
    lsb = 2**(-sfixed_fract)

    xo = np.zeros(iterations+1)
    yo = np.zeros(iterations+1)
    zo = np.zeros(iterations+1)

    xo[0] = xi
    yo[0] = yi
    zo[0] = zi

    for i in range(iterations):
        sigma = -1

        if zo[i] >= 0:
            sigma = 1

        y_shift = quantize_value(sra(yo[i], shift_vector[i], sfixed_fract), lsb)
        x_shift = quantize_value(sra(xo[i], shift_vector[i], sfixed_fract), lsb)
    
        xo[i+1] = quantize_value(xo[i] - sigma * y_shift           , lsb)
        yo[i+1] = quantize_value(yo[i] + sigma * x_shift               , lsb)
        zo[i+1] = quantize_value(zo[i] - sigma * angles_vector[i]   , lsb)

    return xo, yo, zo

def gen_shift_vector(n):
    return np.arange(n)

def gen_k(shift_vector, lsb):
    return quantize_value(np.prod(1 / np.sqrt(1 + np.power(2 * np.ones(len(shift_vector)),(-2 * shift_vector)))),lsb)

def gen_angles_vector(shift_vector, lsb):
    angles_vector = np.arctan(np.power(2 * np.ones(len(shift_vector)),(-shift_vector))) / np.pi
    return quantize_value_vec(angles_vector, lsb)

def get_rotated_vector(phase, sfixed_fract, iterations):

    lsb = 2**(-sfixed_fract)
    shift_vector = gen_shift_vector(iterations)
    angles_vector = gen_angles_vector(shift_vector, lsb)
    k = gen_k(shift_vector, lsb)

    xi = quantize_value(1.0 - lsb, lsb)
    xi = quantize_value(xi * k, lsb)
    yi = quantize_value(0, lsb)
    zi = quantize_value(phase, lsb)

    xo, yo, zo = cordic(xi,yi,zi, angles_vector, shift_vector, iterations, sfixed_fract)

    return xo[iterations], yo[iterations]















