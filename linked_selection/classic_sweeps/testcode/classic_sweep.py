import argparse
import concurrent.futures
import sqlite3
import os
import sys

import fwdpy11
import fwdpy11.conditional_models
import msprime
import numpy as np
import pandas as pd

ALPHAS = [1e3]
N = 1000
L = 2000  # NOTE: may need/want a much larger value
DBNAME = "output/data.sqlite3"


def make_parser():
    parser = argparse.ArgumentParser(
        description="Run a classic model of a sweep from a new mutation.  Analyze variation at a non-recombining region some scaled genetic distance away.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "--nreps",
        default=-1,
        type=int,
        help="Number of replicates per genetic distance.",
    )

    parser.add_argument(
        "--ncores", type=int, default=-1, help="Number of cores/processes to use"
    )

    parser.add_argument(
        "--num_recrates",
        "-r",
        default=10,
        help="Number of 4Nr values to use. These will be evenly-spaced from 0 to 1,000.",
    )

    return parser


def run_sim(rho, alpha, msprime_seed, fwdpy11_seed):
    pdict = {
        "recregions": [
            fwdpy11.PoissonInterval(0, L // 2, rho / 4 / N, discrete=True),
            fwdpy11.PoissonInterval(L // 2, L, 0.0, discrete=True),
        ],
        "nregions": [],
        "sregions": [],
        "gvalue": fwdpy11.Multiplicative(2.0),  # NOTE: scaling may be wrong
        "simlen": 100 * N,
        "rates": (0, 0, None),
    }

    params = fwdpy11.ModelParams(**pdict)

    ts = msprime.sim_ancestry(
        N,
        population_size=N,
        sequence_length=L,
        recombination_rate=msprime.RateMap(
            position=[0, L // 2, L], rate=[rho / 4 / N / L / 2, 0.0]
        ),
        random_seed=msprime_seed,
    )

    # pop = fwdpy11.DiploidPopulation(N, L)

    # fwdpy11.evolvets(fwdpy11.GSLrng(fwdpy11_seed), pop, params, 100)

    pop = fwdpy11.DiploidPopulation.create_from_tskit(ts)
    # fwdpy11.evolvets(fwdpy11.GSLrng(fwdpy11_seed), pop, params, 100)

    assert pop.N == N
    mutation_data = fwdpy11.conditional_models.NewMutationParameters(
        frequency=fwdpy11.conditional_models.AlleleCount(1),
        data=fwdpy11.NewMutationData(effect_size=alpha / 2 / pop.N, dominance=1),
        position=fwdpy11.conditional_models.PositionRange(
            left=0.0, right=np.finfo(float).eps
        ),
    )

    rng = fwdpy11.GSLrng(fwdpy11_seed)
    output = fwdpy11.conditional_models.selective_sweep(
        rng,
        pop,
        params,
        mutation_data,
        fwdpy11.conditional_models.GlobalFixation(),
        return_when_stopping_condition_met=True,
    )
    ts = output.pop.dump_tables_to_tskit()
    rsamples = np.sort(np.random.choice([i for i in ts.samples()], 20, replace=False))
    ts2 = ts.simplify(samples=rsamples).keep_intervals([[L // 2, L]])
    afs = (
        ts2.allele_frequency_spectrum(
            # sample_sets=[rsamples],
            mode="branch",
            span_normalise=True,
            polarised=True,
            windows=[0, L // 2, L],
        )
        # normalize afs back down to a theta of 1.0
        / 4.0
        / float(N)
    )[1]
    # print(afs)
    return afs


if __name__ == "__main__":
    parser = make_parser()
    args = parser.parse_args(sys.argv[1:])

    used_fp11_seeds = {}
    used_msprime_seeds = {}
    fp11_seeds = []
    msprime_seeds = []

    mean_afs = np.zeros(21)

    for i in range(args.nreps):
        msp_seed = np.random.randint(0, np.iinfo(np.uint32).max)
        while msp_seed in used_msprime_seeds:
            msp_seed = np.random.randint(0, np.iinfo(np.uint32).max)
        used_msprime_seeds[msp_seed] = 1
        msprime_seeds.append(msp_seed)
        fp11_seed = np.random.randint(0, np.iinfo(np.uint32).max)
        while fp11_seed in used_fp11_seeds:
            fp11_seed = np.random.randint(0, np.iinfo(np.uint32).max)
        fp11_seeds.append(fp11_seed)

    if os.path.exists(DBNAME):
        os.remove(DBNAME)

    with concurrent.futures.ProcessPoolExecutor(max_workers=args.ncores) as executor:
        futures = {
            executor.submit(run_sim, 100.0, 500, m, f)
            for m, f in zip(msprime_seeds, fp11_seeds)
        }
        for future in concurrent.futures.as_completed(futures):
            afs = future.result()
            df = pd.DataFrame(
                {
                    "eta": [i + 1 for i in range(19)],
                    "count": afs[1:-1],
                    "alpha": [100.0] * 19,
                }
            )
            conn = sqlite3.connect(DBNAME)
            df.to_sql("sfs", conn, index=False, if_exists="append")
