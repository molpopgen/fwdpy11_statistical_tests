import argparse
import pickle
import sys

import numpy as np

import fwdpy11
import fwdpy11.demographic_models.IM
import testutils.two_deme_IM_argument_parser


def build_demography(args):
    """
    Returns the demography, the simulation length, and the
    final total size in each deme.

    The main real work here is to convert the input
    paremeters to match the scaling expected by
    fwdpy11.demographic_models.IM.two_deme_IM:

    1. The input migration rates are in units of 2*Nref
    2. The time since the split is also in units of 2*Nref
    """
    two_deme_IM = fwdpy11.demographic_models.IM.two_deme_IM

    # Rescale input migration rates
    migrates = tuple(i / (2.0 * args.Nref) for i in args.migrates)

    # Change split time from generations/(2*Nref) to
    # generations/Nref.
    dmodel = two_deme_IM(
        args.Nref,
        2.0 * args.tsplit,
        args.split,
        (args.N0, args.N1),
        migrates,
        burnin=20.0,
    )
    simlen = int(dmodel.metadata.split_time + dmodel.metadata.gens_post_split)
    N0 = np.rint(args.N0 * args.Nref).astype(int)
    N1 = np.rint(args.N1 * args.Nref).astype(int)
    return dmodel, simlen, (N0, N1)


def build_parameters_dict(args):
    """
    Returns sim params and the final sizes
    in each deme
    """
    demog, simlen, finalNs = build_demography(args)

    nregions = []
    sregions = []
    recregions = [fwdpy11.PoissonInterval(0, 1, args.rho / (4.0 * args.Nref))]

    rates = (0, 0, None)
    if args.gamma is not None:
        sregions = [
            fwdpy11.ConstantS(0, 1, 1, args.gamma, args.H, scaling=2 * args.Nref)
        ]
        rates = (0, args.theta / (4.0 * args.Nref), None)

    pdict = {
        "nregions": nregions,
        "sregions": sregions,
        "recregions": recregions,
        "rates": rates,
        "gvalue": fwdpy11.Multiplicative(2.0),
        "demography": demog,
        "simlen": simlen,
        "prune_selected": True,
    }

    return pdict, simlen, finalNs


if __name__ == "__main__":
    parser = testutils.two_deme_IM_argument_parser.make_model_builder_parser()
    args = parser.parse_args(sys.argv[1:])

    pdict, simlen, finalNs = build_parameters_dict(args)

    model = {
        "pdict": pdict,
        "Nref": args.Nref,
        "genome_length": 1.0,
        "final_deme_sizes": finalNs,
    }

    with open(args.outdir + "/model.pickle", "wb") as f:
        pickle.dump(model, f)
