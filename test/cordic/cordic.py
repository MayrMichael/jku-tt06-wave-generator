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


    m = 1 # because of circular
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
    
        xo[i+1] = quantize_value(xo[i] - m * sigma * y_shift           , lsb)
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


def test_cordic():
    sfixed_fract = 15

    lsb = 2**(-sfixed_fract)

    assert lsb == 3.051757812500000e-05

    a = -0.625

    assert quantize_value(a,lsb) == -0.6250

    assert sra(a,2,sfixed_fract) == -0.156250000000000

    iterations = 15

    shift_vector = gen_shift_vector(iterations)

    k = gen_k(shift_vector, lsb)
    assert k == 0.607238769531250

    angles_vector = gen_angles_vector(shift_vector, lsb)


    assert angles_vector[13] == 3.051757812500000e-05
    assert angles_vector[12] == 6.103515625000000e-05

    xi = quantize_value(1.0 - lsb, lsb)
    yi = quantize_value(0, lsb)
    zi = quantize_value(0, lsb)

    xi = quantize_value(xi * k, lsb)
    xi = quantize_value(xi - lsb, lsb)

    phase = 0.308807373046875

    zi = quantize_value(zi + phase, lsb)

    xo, yo, zo = cordic(xi,yi,zi, angles_vector,  shift_vector, iterations, sfixed_fract)

    xo_m = np.asarray([0.607177734375000,	0.607177734375000,	0.303588867187500,	0.531280517578125,	0.635620117187500,	0.587615966796875,	0.562377929687500,	0.575286865234375,	0.568908691406250,	0.565704345703125,	0.564117431640625,	0.564910888671875,	0.565307617187500,	0.565124511718750,	0.565032958984375,	0.565002441406250])

    assert (xo == xo_m).all()

    yo_m = np.asarray([0,	0.607177734375000,	0.910766601562500,	0.834869384765625,	0.768463134765625,	0.808166503906250,	0.826507568359375,	0.817749023437500,	0.822235107421875,	0.824432373046875,	0.825531005859375,	0.824981689453125,	0.824707031250000,	0.824829101562500,	0.824890136718750,	0.824920654296875])

    assert (yo == yo_m).all()

    zo_m = np.asarray([0.308807373046875,	0.0588073730468750,	-0.0887756347656250,	-0.0108032226562500,	0.0287780761718750,	0.00891113281250000,	-0.00100708007812500,	0.00393676757812500,	0.00146484375000000,	0.000244140625000000,	-0.000366210937500000,	-6.10351562500000e-05,	9.15527343750000e-05,	3.05175781250000e-05,	0,	0])

    assert (zo == zo_m).all()

def get_rotated_vector(phase, sfixed_fract, iterations):

    lsb = 2**(-sfixed_fract)
    shift_vector = gen_shift_vector(iterations)
    angles_vector = gen_angles_vector(shift_vector, lsb)
    k = gen_k(shift_vector, lsb)
    xi = quantize_value(1.0 - lsb, lsb)
    yi = quantize_value(0, lsb)
    zi = quantize_value(0, lsb)
    xi = quantize_value(xi * k, lsb)
    
    zi = quantize_value(zi + phase, lsb)

    xo, yo, zo = cordic(xi,yi,zi, angles_vector, shift_vector, iterations, sfixed_fract)

    return xo[iterations], yo[iterations]















