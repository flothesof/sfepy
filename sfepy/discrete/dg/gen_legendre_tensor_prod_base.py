from argparse import ArgumentParser
from sympy import symbols
from sympy import jacobi_poly as jacobi_P
from sympy import expand_mul as expand
from sympy import simplify

from toolz import reduce, map
from operator import mul

import numpy as np

from sfepy.base.ioutils import InDir
from sfepy.discrete.dg.dg_basis import iter_by_order, get_n_el_nod

helps = {
    'max_order' :
        'maximum order of polynomials [default: %(default)s]',
    'output_dir':
        'output directory',
}


def main():
    print("WARNING! this script is deprecated and does not provide tensor basis"
          + "coefficients and exponents truly used in sfepy.")
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('-m', '--max-order', metavar='order', type=int,
                        action='store', dest='max_order',
                        default=10, help=helps['max_order'])
    parser.add_argument("-e", "--extended", action="store_true", default=False)
    parser.add_argument('output_dir', help=helps['output_dir'])
    options = parser.parse_args()

    extended = options.extended
    indir = InDir(options.output_dir)

    r, s = symbols("r, s")
    x, y = symbols("x, y")
    order = options.max_order
    dim = 2
    n_el_nod = get_n_el_nod(order, dim, extended)

    tensorP = []
    exponentM = np.zeros((n_el_nod, 3), dtype=np.int32)
    coefM = np.zeros((n_el_nod, n_el_nod))
    exponentList = []
    for m, idx in enumerate(iter_by_order(order, dim, extended)):
        # print(m, idx)
        exponentM[m, :dim] = idx
        # print("P_{} = {}".format(m, pa*pb))
        polrs = jacobi_P(idx[0], 0, 0, r) * jacobi_P(idx[1], 0, 0, s)
        # print("P_{} = {}".format(m, polrs))
        # polxy = expand(polrs.subs(r, 2*x - 1).subs(s, 2*y - 1))
        polxy = expand(polrs.subs(r, x).subs(s, y))

        tensorP.append(simplify(polxy))
        exponentList.append(x ** idx[0] * y ** idx[1])
        for j, exponent in enumerate(exponentList):
            coefM[m, j] = tensorP[m].as_coefficients_dict()[exponent]
        print("P_{}{} = {}".format(m, idx, tensorP[m]))
        print()

    np.savetxt(indir("legendre2D_tensor{}_expos.txt".format("_ext" if extended else "")), exponentM, fmt="%s")
    # TODO are coefs always integers?
    np.savetxt(indir("legendre2D_tensor{}_coefs.txt".format("_ext" if extended else "")), coefM, fmt="%d")


if __name__ == '__main__':
    main()
