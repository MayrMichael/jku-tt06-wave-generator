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


def square_puls(sfixed_fract, phase, threshold, n_samples):
    lsb = 2**(-sfixed_fract)

    calc_values = np.zeros(n_samples)
    counter = 0

    for i in range(0, n_samples):
        counter = quantize_value(counter + phase , lsb)

        if counter >= threshold:
            calc_values[i] = quantize_value(1-lsb, lsb)
        else:
            calc_values[i] = quantize_value(-1 + lsb, lsb)

    return calc_values