import numpy as np
import triangle
import matplotlib.pyplot as plt

if __name__ == '__main__':
    sfixed_fract = 7
    
    n_samples = 1000

    lsb = 2**(-sfixed_fract)

    amplitude = 1 - 40 * lsb
    phase = 0.01
    threshold = 0.4
    data_saw = triangle.sawtooth(sfixed_fract, phase, amplitude, n_samples)

    data_tri = triangle.triangle(sfixed_fract, phase, amplitude, n_samples)


    x = np.arange(n_samples)

    lsb = 2**(-sfixed_fract)

    plt.plot(x, data_tri)
    plt.plot(x, data_saw)
    
    plt.show()