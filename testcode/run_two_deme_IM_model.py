import concurrent.futures
import pickle
import sys

import matplotlib.pyplot as plt
import moments
import numpy as np
import seaborn as sns

import fwdpy11
import testutils.analysis_tools
import testutils.two_deme_IM_argument_parser


def runsim(model, num_subsamples, nsam, seed):
    rng = fwdpy11.GSLrng(seed)
    pop = fwdpy11.DiploidPopulation(model["Nref"], model["genome_length"])
    fwdpy11.evolvets(rng, pop, fwdpy11.ModelParams(**model["pdict"]), 100)
    if model["mutations_are_neutral"] is True:
        fwdpy11.infinite_sites(rng, pop, model["theta"] / 4 / model["Nref"])
    mean_fst = 0.0
    deme_zero_fs = np.zeros(2 * args.nsam - 1)
    deme_one_fs = np.zeros(2 * args.nsam - 1)
    for _ in range(num_subsamples):
        fs = testutils.analysis_tools.tskit_fs(pop, nsam)
        fs = moments.Spectrum(fs)
        mean_fst += fs.Fst()
        deme_zero_fs += fs.marginalize([1]).data[1:-1]
        deme_one_fs += fs.marginalize([0]).data[1:-1]

    mean_fst /= num_subsamples
    deme_zero_fs /= num_subsamples
    deme_one_fs /= num_subsamples

    return mean_fst, deme_zero_fs, deme_one_fs


if __name__ == "__main__":
    parser = testutils.two_deme_IM_argument_parser.make_model_runner_parser()
    parser.add_argument(
        "--num_subsamples", type=int, default=None, help="Number of subsamples to take"
    )
    args = parser.parse_args(sys.argv[1:])

    with open(args.infile, "rb") as f:
        model = pickle.load(f)

    initial_seed = np.random.randint(0, np.iinfo(np.uint32).max, 1)[0]
    np.random.seed(initial_seed)

    seeds = np.random.randint(0, np.iinfo(np.uint32).max, args.nreps)

    fsta = np.zeros(args.nreps)
    mean_deme_zero_fs = np.zeros(2 * args.nsam - 1)
    mean_deme_one_fs = np.zeros(2 * args.nsam - 1)
    idx = 0
    with concurrent.futures.ProcessPoolExecutor(max_workers=args.nworkers) as e:
        futures = {
            e.submit(runsim, model, args.num_subsamples, args.nsam, i) for i in seeds
        }
        for fut in concurrent.futures.as_completed(futures):
            fst, d0, d1 = fut.result()
            fsta[idx] = fst
            idx += 1
            mean_deme_zero_fs += d0
            mean_deme_one_fs += d1

    mean_deme_zero_fs /= args.nreps
    mean_deme_one_fs /= args.nreps

    with open(args.outdir + "/caption.rst", "w") as f:
        f.write(f"The initial_seed was {initial_seed}.\n")
        f.write("The model details are:\n\n::\n\n")
        mp = fwdpy11.ModelParams(**model["pdict"])
        for i in mp.asblack().split("\n"):
            f.write(f"\t{i}\n")
        f.write("\n")

    with open(args.outdir + "/fst.np", "wb") as f:
        fsta.tofile(f)
    with open(args.outdir + "/deme0.np", "wb") as f:
        mean_deme_zero_fs.tofile(f)
    with open(args.outdir + "/deme1.np", "wb") as f:
        mean_deme_one_fs.tofile(f)
