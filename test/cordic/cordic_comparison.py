import numpy as np
import matplotlib.pyplot as plt
import cordic

if __name__ == '__main__':
    sfixed_fract = 15
    iterations = 15
    phase = 0.308807373046875

    xy_15_15 = cordic.get_rotated_vector(phase, sfixed_fract, iterations)

    sfixed_fract = 7

    xy_8_8 = cordic.get_rotated_vector(phase, sfixed_fract, iterations)

    iterations = 6
    xy_8_6 = cordic.get_rotated_vector(phase, sfixed_fract, iterations)

    xy_np =  (np.cos(phase * np.pi), np.sin(phase * np.pi))


    lsb = 2**(-7)

    xy_15_15 = cordic.quantize_value_vec(xy_15_15, lsb)
    xy_8_8 = cordic.quantize_value_vec(xy_8_8, lsb)
    xy_8_6 = cordic.quantize_value_vec(xy_8_6, lsb)
    xy_np_q = cordic.quantize_value_vec(xy_np, lsb)


    M = np.array([xy_np, xy_np_q, xy_8_8, xy_8_6, xy_15_15 ])

    print(xy_np)
    print(xy_np_q)
    print(xy_8_8)
    print(xy_8_6)
    print(xy_15_15)

    rows,cols = M.T.shape

    #Get absolute maxes for axis ranges to center origin
    #This is optional
    maxes = 1.1*np.amax(abs(M), axis = 0)

    for i,l in enumerate(range(0,cols)):
        xs = [0,M[i,0]]
        ys = [0,M[i,1]]
        plt.plot(xs,ys, 'o--')

    #plt.plot(0,0,'ok') #<-- plot a black point at the origin
    plt.axis('equal')  #<-- set the axes to the same scale
    plt.xlim([-1.2,1.2]) #<-- set the x axis limits
    plt.ylim([-1.2,1.2]) #<-- set the y axis limits
    plt.legend( ['original','original quant 8 Bit', '8 Bits, 8 Iterations', '8 Bits, 6 Iterations','16 Bits, 15 Iterations']) #<-- give a legend
    plt.grid(b=True, which='major') #<-- plot grid lines
    plt.show()