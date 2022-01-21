from dataclasses import dataclass
import sqlite3
import concurrent.futures
import argparse
import pandas as pd
import sys

import numpy as np
from testutils import ALPHAS, DOMINANCE, SCALING

DBNAME = "output/sfs_data.sqlite3"


@dataclass
class Result:
    fixation_time: int
    alpha: float


def make_parser():
    parser = argparse.ArgumentParser(
        description="Get the distribution of fixation times via naive simulation in Python.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "--popsize", "-N", type=int, default=1000, help="Diploid population size"
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

    return parser


def simulate(N, alpha, generator):
    s = alpha / 2 / N

    # NOTE: will have to confirm these fitnesses
    wAA = 1
    wAa = 1 + DOMINANCE * s
    waa = 1 + SCALING * s

    done = False

    rv = -1

    while not done:
        c = 1
        g = 0
        while c > 0 and c < 2 * N:
            q = c / 2.0 / N
            p = 1.0 - q

            wbar = wAA * p ** 2.0 + 2.0 * wAa * p * q + waa * q ** 2.0
            dq = p * q * (p * (wAa - wAA) + q * (waa - wAa)) / wbar

            c = generator.binomial(2 * N, q + dq, 1)[0]
            g += 1

        if c == 2 * N:
            rv = g
            done = True

    return rv


def run_sim(N, alpha, seed):
    generator = np.random.default_rng(seed)

    t = simulate(N, alpha, generator)

    return t, alpha


def dispatch_work(args):
    params = []
    used_seeds = {}
    for a in ALPHAS:
        for _ in range(args.nreps):
            seed = np.random.randint(0, np.iinfo(np.uint32).max)
            while seed in used_seeds:
                seed = np.random.randint(0, np.iinfo(np.uint32).max)
            used_seeds[seed] = 1
            params.append((a, seed))

    results = []

    with concurrent.futures.ProcessPoolExecutor(max_workers=args.ncores) as executor:
        futures = {
            executor.submit(run_sim, args.popsize, alpha, seed)
            for alpha, seed in params
        }
        for future in concurrent.futures.as_completed(futures):
            t, alpha = future.result()
            results.append(Result(t, alpha))

    df = pd.DataFrame(results)

    with sqlite3.connect(DBNAME) as conn:
        df.to_sql("python_fixation_times", conn, index=False, if_exists="fail")


if __name__ == "__main__":
    parser = make_parser()
    args = parser.parse_args(sys.argv[1:])

    dispatch_work(args)
