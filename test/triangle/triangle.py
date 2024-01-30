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

def triangle(sfixed_fract, phase, amplitude, n_samples):
    lsb = 2**(-sfixed_fract)
    
    calc_values = np.zeros(n_samples)
    counter = quantize_value(phase, lsb)
    calc_values[0] = counter
    old_counter = counter

    reverse = False
    rev_counter = 0

    for i in range(1, n_samples):
        if counter <= amplitude:
            counter = quantize_value(counter + phase , lsb)
        else:
            counter = quantize_value(counter * (-1), lsb)

        inter_counter = counter

        if np.signbit(counter) != np.signbit(old_counter):
            if rev_counter == 0:
                reverse = not reverse
                rev_counter = 1
            else:
                rev_counter = 0

        if reverse:
            calc_values[i] = quantize_value(inter_counter * (-1), lsb)
        else:
            calc_values[i] = quantize_value(inter_counter, lsb)

        old_counter = counter

    return calc_values
