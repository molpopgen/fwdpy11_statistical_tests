import concurrent.futures
import pickle
import sys

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

import fwdpy11
import testutils.two_deme_IM_argument_parser


def runsim(model, seed):
    rng = fwdpy11.GSLrng(seed)
    pop = fwdpy11.DiploidPopulation(model["Nref"], model["genome_length"])
    fwdpy11.evolvets(rng, pop, fwdpy11.ModelParams(**model["pdict"]), 100)
    fwdpy11.infinite_sites(rng, pop, 1.0)
    return len(pop.tables.mutations)


if __name__ == "__main__":
    parser = testutils.two_deme_IM_argument_parser.make_model_runner_parser()
    args = parser.parse_args(sys.argv[1:])

    with open(args.infile, "rb") as f:
        model = pickle.load(f)

    initial_seed = np.random.randint(0, np.iinfo(np.uint32).max, 1)[0]
    np.random.seed(initial_seed)

    seeds = np.random.randint(0, np.iinfo(np.uint32).max, args.nreps)

    results = []
    with concurrent.futures.ProcessPoolExecutor(max_workers=args.nworkers) as e:
        futures = {e.submit(runsim, model, i) for i in seeds}
        for fut in concurrent.futures.as_completed(futures):
            result = fut.result()
            results.append(result)

    with open(args.outdir + "/caption.rst", "w") as f:
        f.write(f"The initial_seed was {initial_seed}\n")
        f.write("The model details are:\n\n::\n\n")
        mp = fwdpy11.ModelParams(**model["pdict"])
        for i in mp.asblack().split("\n"):
            f.write(f"\t{i}\n")
        f.write("\n")

    d = sns.distplot(results)
    plt.savefig(args.outdir + "/S.png")
