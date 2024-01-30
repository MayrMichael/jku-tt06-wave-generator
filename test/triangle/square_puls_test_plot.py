import numpy as np
import square_puls
import matplotlib.pyplot as plt

if __name__ == '__main__':
    sfixed_fract = 7
    
    n_samples = 1000

    lsb = 2**(-sfixed_fract)

    amplitude = 1 - 40 * lsb
    phase = 0.01
    threshold = 0.4

    data_sq = square_puls.square_puls(sfixed_fract, phase, threshold, n_samples)

    x = np.arange(n_samples)

    lsb = 2**(-sfixed_fract)

    plt.plot(x, data_sq)    
    plt.show()