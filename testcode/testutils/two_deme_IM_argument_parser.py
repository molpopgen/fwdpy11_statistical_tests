import argparse


def make_model_builder_parser():
    ADHF = argparse.ArgumentDefaultsHelpFormatter
    parser = argparse.ArgumentParser(
        "Building two deme IM models", formatter_class=ADHF
    )
    parser.add_argument(
        "--split", "-s", type=float, help="Fraction that splits into deme 0"
    )
    parser.add_argument(
        "--tsplit",
        "-T",
        type=float,
        help="Time since population split," " in units of 2*Nref generations",
    )
    parser.add_argument("--seed", type=int, help="Random number seed")

    parser.add_argument(
        "--outdir", type=str, default=None, help="Output directory name"
    )

    optional = parser.add_argument_group("Optional")
    optional.add_argument(
        "--Nref", type=int, default=1000, help="Ancestral population size"
    )
    optional.add_argument(
        "--N0",
        type=float,
        default=1.0,
        help="Contemporary size of deme 0, relative to Nref",
    )
    optional.add_argument(
        "--N1",
        type=float,
        default=1.0,
        help="Contemporary size of deme 1, relative to Nref",
    )
    optional.add_argument("--gamma", type=float, help="2Ns")
    # Require 0 <= h <= 2
    optional.add_argument("-H", type=float, default=1.0, help="Dominance")
    optional.add_argument(
        "--migrates",
        "-M",
        type=float,
        nargs=2,
        default=[0.0, 0.0],
        help="Migration rates, scaled by 2*Nref.",
    )
    optional.add_argument(
        "--nsam",
        type=int,
        default=15,
        help="Number of diploids to sample from each deme",
    )
    optional.add_argument(
        "--theta",
        type=float,
        default=1.0,
        help="Scaled mutation rate. " "Danger zone with selection :).",
    )
    optional.add_argument(
        "--rho",
        type=float,
        default=1e3,
        help="Scaled recombination rate, rho = 4*Nref*r",
    )
    return parser


def make_model_runner_parser():
    ADHF = argparse.ArgumentDefaultsHelpFormatter
    parser = argparse.ArgumentParser("Running two deme IM models", formatter_class=ADHF)

    parser.add_argument("--infile", type=str, default=None, help="Pickled model file")
    parser.add_argument(
        "--outdir", type=str, default=None, help="Output directory name"
    )
    parser.add_argument(
        "--nreps", type=int, default=None, help="Number of replicates to run"
    )
    parser.add_argument(
        "--nworkers", type=int, default=None, help="Number of worker processes"
    )

    return parser
