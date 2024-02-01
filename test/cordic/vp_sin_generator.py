import numpy as np
import vp_cordic_iterative

def sin_gen(sfixed_fract, phase, iterations, n_samples):

    calc_values, xc_values, yc_values, zc_values, xi_values, yi_values, zi_values = sin_gen_debug(sfixed_fract, phase, iterations, n_samples)
    return calc_values


def sin_gen_debug(sfixed_fract, phase, iterations, n_samples):

    calc_values = np.zeros(n_samples)

    xc_values = np.zeros(n_samples)
    yc_values = np.zeros(n_samples)
    zc_values = np.zeros(n_samples)

    xi_values = np.zeros(n_samples)
    yi_values = np.zeros(n_samples)
    zi_values = np.zeros(n_samples)

    lsb = 2**(-sfixed_fract)
    shift_vector = vp_cordic_iterative.gen_shift_vector(iterations)
    angles_vector = vp_cordic_iterative.gen_angles_vector(shift_vector, lsb)
    k = vp_cordic_iterative.gen_k(shift_vector, lsb)

    xi = vp_cordic_iterative.quantize_value(1.0 - lsb, lsb)
    yi = vp_cordic_iterative.quantize_value(0, lsb)
    zi = vp_cordic_iterative.quantize_value(0, lsb)

    xi = vp_cordic_iterative.quantize_value(xi * k, lsb)
    xi = vp_cordic_iterative.quantize_value(xi - lsb, lsb)

    for i in range(n_samples):
        zi = vp_cordic_iterative.quantize_value(zi + phase, lsb)

        xc = xi
        yc = yi
        zc = zi

        xi_values[i] = xc
        yi_values[i] = yc
        zi_values[i] = zc

        if zi < -0.5:
            zc = zi + 0.5 
            xc = yi
            yc = -xi
        elif zi > 0.5:
            zc = zi - 0.5
            xc = -yi
            yc = xi

        xc = vp_cordic_iterative.quantize_value(xc, lsb)
        yc = vp_cordic_iterative.quantize_value(yc, lsb)
        zc = vp_cordic_iterative.quantize_value(zc, lsb)

        xc_values[i] = xc
        yc_values[i] = yc
        zc_values[i] = zc

        xo, yo, zo = vp_cordic_iterative.cordic(xc,yc,zc, angles_vector, shift_vector, iterations, sfixed_fract)
        
        calc_values[i] = yo[iterations]

    return calc_values, xc_values, yc_values, zc_values, xi_values, yi_values, zi_values










