import argparse
import concurrent.futures
import os
import subprocess
import sys

import demes
import demesdraw
import fwdpy11
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import moments
import numpy as np

RHO = 100.0  # 1e4
THETA = 10000.0


def make_parser():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--yaml", type=str, default=None, help="YAML file containing demographic model"
    )
    parser.add_argument(
        "--burnin",
        type=int,
        default=10,
        help="Burnin (integer multiple of ancestral (meta-)population size)",
    )

    parser.add_argument(
        "--nsam",
        type=int,
        default=20,
        help="Number of diploids to sample from each deme at the end of a simulation.",
    )

    parser.add_argument(
        "--seed", type=int, default=None, help="Global random number generator seed"
    )

    parser.add_argument(
        "--nreps",
        type=int,
        default=None,
        help="Number of forward simulation replicates",
    )

    parser.add_argument("--nthreads", type=int, default=None, help="Number of threads")

    return parser


def validate_args(args):
    if args.yaml is None:
        raise ValueError("No YAML file specified")

    if args.nreps is None or args.nreps < 1:
        raise ValueError("nreps must be >= 1")


def get_final_demes(dg):
    return [i.name for i in dg.demes if i.end_time == 0]


def integrate_fs(args):
    dg = demes.load(args.yaml)

    final_demes = get_final_demes(dg)

    return moments.Spectrum.from_demes(
        dg, final_demes, [2 * args.nsam] * len(final_demes)
    )


def runsim(args, simseed, npseed):
    dg = demes.load(args.yaml)

    final_demes = get_final_demes(dg)

    demog = fwdpy11.discrete_demography.from_demes(dg, burnin=args.burnin)

    final_deme_ids = sorted(
        [
            i
            for i in demog.metadata["deme_labels"]
            if demog.metadata["deme_labels"][i] in final_demes
        ]
    )

    initial_sizes = [
        demog.metadata["initial_sizes"][i]
        for i in sorted(demog.metadata["initial_sizes"].keys())
    ]
    recrate = RHO / (4.0 * initial_sizes[0])

    pdict = {
        "nregions": [],
        "sregions": [],
        "recregions": [fwdpy11.PoissonInterval(0, 1, recrate)],
        "gvalue": fwdpy11.Multiplicative(2.0),
        "rates": (0.0, 0.0, None),
        "simlen": demog.metadata["total_simulation_length"],
        "demography": demog,
    }
    params = fwdpy11.ModelParams(**pdict)
    pop = fwdpy11.DiploidPopulation(initial_sizes, 1.0)

    # FIXME: need seed as input argument to this fxn
    rng = fwdpy11.GSLrng(simseed)
    np.random.seed(npseed)

    fwdpy11.evolvets(rng, pop, params, 100)

    nmuts = fwdpy11.infinite_sites(rng, pop, THETA / (4.0 * initial_sizes[0]))

    md = np.array(pop.diploid_metadata, copy=False)
    sample_nodes = []
    for i in final_deme_ids:
        w = np.where(md["deme"] == i)
        s = np.random.choice(w[0], args.nsam, replace=False)
        sample_nodes.append(md["nodes"][s].flatten())

    fs = pop.tables.fs(sample_nodes)

    return fs


def make_plot(sim_fs, integrated_fs, args, initial_seed):
    ndemes = len(integrated_fs.shape)

    outfile = os.path.basename(args.yaml).replace(".yml", "_residuals.png")

    fig = plt.Figure()

    if ndemes == 2:
        moments_sim_fs = moments.Spectrum(sim_fs.todense())
        moments.Plotting.plot_2d_comp_Poisson(
            integrated_fs,
            moments_sim_fs,
            show=False,
            fig_num=plt.gcf().number,
        )
        # simfs = os.path.basename(args.yaml).replace("yml", "mean_sim_fs")
        # moments_sim_fs.to_file(simfs)
        # simfs = os.path.basename(args.yaml).replace("yml", "integrated_fs")
        # integrated_fs.to_file(simfs)
    elif ndemes == 1:
        moments_sim_fs = moments.Spectrum(sim_fs.data[:-1])
        moments.Plotting.plot_1d_comp_Poisson(
            integrated_fs[:-1],
            moments_sim_fs,
            show=False,
            fig_num=plt.gcf().number,
        )
        # simfs = os.path.basename(args.yaml).replace("yml", "mean_sim_fs")
        # moments_sim_fs.to_file(simfs)
        # simfs = os.path.basename(args.yaml).replace("yml", "integrated_fs")
        # integrated_fs.to_file(simfs)
    else:
        raise NotImplementedError(f"Plotting not implemented for {ndemes} demes.")

    plt.gcf().suptitle(f"No. reps = {args.nreps}, seed = {initial_seed}")
    plt.gcf().tight_layout()
    plt.savefig(outfile)
    return outfile


def draw_model(args):
    dg = demes.load(args.yaml)
    outfile = os.path.basename(args.yaml).replace(".yml", "_draw.png")
    _ = demesdraw.tubes(dg)
    plt.savefig(outfile)
    return outfile


def update_fs(current_fs, new_fs, ndemes):
    if current_fs is None:
        if ndemes == 1:
            return np.array(new_fs.data, dtype=np.float64)
        elif ndemes == 2:
            return new_fs  # .astype(np.float64)

    if ndemes == 1:
        return current_fs + np.array(new_fs.data, dtype=np.float64)
    elif ndemes == 2:
        return current_fs + new_fs  # .astype(np.float64)


if __name__ == "__main__":
    parser = make_parser()

    args = parser.parse_args(sys.argv[1:])

    validate_args(args)

    integrated_fs = integrate_fs(args)
    ndemes = len(integrated_fs.shape)

    initial_seed = np.random.randint(0, np.iinfo(np.uint32).max, 1)[0]
    np.random.seed(initial_seed)
    simseeds = []
    npseeds = []

    for i in range(args.nreps):
        s = np.random.randint(0, np.iinfo(np.uint32).max, 1)
        while s in simseeds:
            s = np.random.randint(0, np.iinfo(np.uint32).max, 1)
        simseeds.append(s)
        s = np.random.randint(0, np.iinfo(np.uint32).max, 1)
        while s in npseeds:
            s = np.random.randint(0, np.iinfo(np.uint32).max, 1)
        npseeds.append(s)

    mean_fs = None
    with concurrent.futures.ProcessPoolExecutor(max_workers=args.nthreads) as e:
        futures = {e.submit(runsim, args, i, j) for i, j in zip(simseeds, npseeds)}
        for f in concurrent.futures.as_completed(futures):
            sim_fs = f.result()
            mean_fs = update_fs(mean_fs, sim_fs, ndemes)

    mean_fs = mean_fs.astype(np.float64) / float(args.nreps)
    residfile = make_plot(mean_fs, integrated_fs * THETA, args, initial_seed)
    drawfile = draw_model(args)
    subprocess.call(
        f"convert {residfile} {drawfile} +append {os.path.basename(args.yaml).replace('.yml','.png')}",
        shell=True,
    )
