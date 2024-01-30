import numpy as np
import cordic
import sin_generator
import matplotlib.pyplot as plt

if __name__ == '__main__':
    sfixed_fract = 7
    # phase = 0.308807373046875
    phase = 0.01
    iterations = 6
    n_samples = 1000

    data = sin_generator.sin_gen(sfixed_fract, phase, iterations, n_samples)

    x = np.arange(n_samples)

    lsb = 2**(-sfixed_fract)

    y = np.sin(phase * np.pi * (x + 1))

    y_q = cordic.quantize_value_vec(y,lsb)

    plt.plot(x, data)
    plt.show()