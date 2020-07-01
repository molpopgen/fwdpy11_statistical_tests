import sys

import moments
import numpy as np

import testutils.two_deme_IM_argument_parser


def IM_moments(params, ns, gamma=0.0, h=0.5):
    """
    Expected FS for IM model with selection

    ns: sample sizes, given as [ns1, ns2]
    s: frac that splits into deme 1 (1-s into deme 2)
    nu1/nu2: contemporary population sizes, with exponenential size change
    T: time between split and now (in 2Nref generations)
    m12/m21: migration rates, scaled by 2Nref
             mij is rate from j into i

    The mutation rate theta=4*N_ref*u is assumed to be 1.

    ns: the sample sizes (don't have to be equal) given as list of length 2

    gamma: pop-size scaled selection coefficient (2Ns), default 0
    h: dominance coefficient, default 0.5

    Note that when integrating, gamma and h must be passed as lists of same
    length as number of demes, with each entry specifying the coefficient in
    each deme. If they are all the same, pass
        `gamma=[gamma, gamma, ..., gamma], h=[h, h, ..., h]`
    where the lengths are equal to the number of demes.

    gamma = 2*N_ref*s, with the interpretation of fitnesses:
        aa : 1
        Aa : 1+2hs
        AA : 1+2s
    """
    s, nu1, nu2, T, m12, m21 = params
    # equilibrium frequency spectrum
    sts = moments.LinearSystem_1D.steady_state_1D(ns[0] + ns[1], gamma=gamma, h=h)
    fs = moments.Spectrum(sts)
    # split into two demes
    fs = moments.Manips.split_1D_to_2D(fs, ns[0], ns[1])
    # define size change function
    A, B = 1.0, 1.0
    if s is not None:
        A, B = 1.0 - s, s

    def nu1_func(t):
        return A * np.exp(np.log(nu1 / A) * t / T)

    def nu2_func(t):
        return B * np.exp(np.log(nu2 / B) * t / T)

    def nu_func(t):
        return [nu1_func(t), nu2_func(t)]

    # integrate for time T
    fs.integrate(
        nu_func, T, m=np.array([[0, m12], [m21, 0]]), gamma=[gamma, gamma], h=[h, h]
    )
    return fs


if __name__ == "__main__":
    parser = testutils.two_deme_IM_argument_parser.make_model_builder_parser()
    parser.add_argument(
        "--fsfile", type=str, default=None, help="File name to write out the fs"
    )
    parser.add_argument(
        "--nsam", type=int, default=None, help="Sample size (no. diploids)"
    )
    args = parser.parse_args(sys.argv[1:])
    moments_params = (
        args.split,
        args.N0,
        args.N1,
        args.tsplit,
        args.migrates[1],
        args.migrates[0],
    )
    moments_nsam = (2 * args.nsam, 2 * args.nsam)
    mgamma = args.gamma
    if mgamma is None:
        mgamma = 0.0
    moments_fs = IM_moments(moments_params, moments_nsam, mgamma, args.H / 2.0)

    with open(args.fsfile, "w") as f:
        moments_fs.to_file(f)
