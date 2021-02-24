import argparse
import sys

import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import moments
import numpy as np
import seaborn as sns


def plot_fst(fst, moments_fs, ax):
    moments_Fst = moments_fs.Fst()
    d = sns.distplot(fst, ax=ax)
    ax.set_title(f"Mean from sims = {fst.mean():.4f}.\nExpectation = {moments_Fst:.4f}.")
    ax.set_xlabel(r"$F_{st}$")
    ax.axvline(moments_fs.Fst())


def plot_marginal_fs(fs, deme, mfs, ax):
    ax.plot([i for i in range(len(fs))], fs, "bo", label="fwdpy11")
    ax.plot([i for i in range(len(fs))], mfs.data[1:-1], "go", label="moments")
    ax.set_xlabel("Derived frequency")
    ax.set_title(f"Deme {deme}")
    ax.legend()


def make_parser():
    ADHF = argparse.ArgumentDefaultsHelpFormatter
    parser = argparse.ArgumentParser(
        "Plots for two deme IM model tests.", formatter_class=ADHF
    )

    parser.add_argument(
        "--workdir",
        type=str,
        default=None,
        help="Directory where the input/output happens",
    )

    parser.add_argument(
        "--moments_theta",
        type=float,
        default=None,
        help="Scaling factor for moments fs",
    )

    return parser


if __name__ == "__main__":
    parser = make_parser()
    args = parser.parse_args(sys.argv[1:])

    # Results from the foward sim
    fst = np.memmap(args.workdir + "/fst.np", np.float)
    deme0 = np.memmap(args.workdir + "/deme0.np", np.float)
    deme1 = np.memmap(args.workdir + "/deme1.np", np.float)

    # moments reults
    moments_fs = moments.Spectrum.from_file(args.workdir + "/moments.fs")

    fig = plt.figure(figsize=(12, 4), constrained_layout=True)
    gs = gridspec.GridSpec(nrows=1, ncols=3, figure=fig)
    axes = (fig.add_subplot(gs[0]), fig.add_subplot(gs[1]), fig.add_subplot(gs[2]))

    plot_marginal_fs(
        deme0, 0, args.moments_theta * moments_fs.marginalize([1]), axes[0]
    )
    plot_marginal_fs(
        deme1, 1, args.moments_theta * moments_fs.marginalize([0]), axes[1]
    )
    plot_fst(fst, moments_fs, axes[2])
    plt.savefig(args.workdir + "/results.png")
