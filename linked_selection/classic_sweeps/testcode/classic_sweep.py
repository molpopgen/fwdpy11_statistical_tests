import argparse
from typing import List
from dataclasses import dataclass, field, asdict
import concurrent.futures
import sqlite3
import os
import sys

import fwdpy11
import fwdpy11.conditional_models
import msprime
import numpy as np
import pandas as pd

MIN_ALPHA = 10
MAX_ALPHA = 10000
MIN_RHO = 10
MAX_RHO = 10000
L = 2000  # NOTE: may need/want a much larger value

DBNAME = "output/data.sqlite3"


@dataclass
class ForwardSimDataArrays:
    # Arrays to store data
    eta: List[int] = field(default_factory=list)
    count: List[float] = field(default_factory=list)
    alpha: List[float] = field(default_factory=list)
    rho: List[float] = field(default_factory=list)

    def len(self):
        return len(self.eta)

    def to_df(self):
        df = pd.DataFrame({"eta": self.eta, "count": self.count, "alpha": self.alpha})
        return df

    def clear(self):
        self.eta.clear()
        self.count.clear()
        self.alpha.clear()
        self.rho.clear()

    def dump(self, dbname):
        conn = sqlite3.connect(dbname)
        df = self.to_df()
        df.to_sql("sfs", conn, index=False, if_exists="append")
        self.clear()

    def extend(self, sfs, simparams):
        n = len(sfs) - 2
        self.eta.extend([i + 1 for i in range(n)])
        self.alpha.extend([simparams.alpha] * n)
        self.rho.extend([simparams.rho] * n)
        self.count.extend(sfs[1:-1].tolist())


@dataclass
class SimParams:
    N: int
    rho: float
    alpha: float
    msprime_seed: int
    fwdpy11_seed: int


def make_parser():
    parser = argparse.ArgumentParser(
        description="Run a classic model of a sweep from a new mutation.  Analyze variation at a non-recombining region some scaled genetic distance away.",
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

    parser.add_argument(
        "--num_recrates",
        "-r",
        default=10,
        help="Number of 4Nr values to use. These will be evenly-spaced from 10 to 10,000.",
    )

    parser.add_argument(
        "--num-alphas",
        type=int,
        default=5,
        help="Number of values of 2Ns to use.  Values will be evenly-spaced from 100 to 10,000.",
    )

    return parser


def run_sim(simparams: SimParams):
    pdict = {
        "recregions": [
            fwdpy11.PoissonInterval(0, L // 2, rho / 4 / simparams.N, discrete=True),
            fwdpy11.PoissonInterval(L // 2, L, 0.0, discrete=True),
        ],
        "nregions": [],
        "sregions": [],
        "gvalue": fwdpy11.Multiplicative(2.0),  # NOTE: scaling may be wrong
        "simlen": 100 * simparams.N,
        "rates": (0, 0, None),
    }

    params = fwdpy11.ModelParams(**pdict)

    ts = msprime.sim_ancestry(
        simparams.N,
        population_size=simparams.N,
        sequence_length=L,
        recombination_rate=msprime.RateMap(
            position=[0, L // 2, L], rate=[rho / 4 / simparams.N / L / 2, 0.0]
        ),
        random_seed=simparams.msprime_seed,
    )

    pop = fwdpy11.DiploidPopulation.create_from_tskit(ts)

    assert pop.N == simparams.N
    mutation_data = fwdpy11.conditional_models.NewMutationParameters(
        frequency=fwdpy11.conditional_models.AlleleCount(1),
        data=fwdpy11.NewMutationData(effect_size=alpha / 2 / pop.N, dominance=1),
        position=fwdpy11.conditional_models.PositionRange(
            left=0.0, right=np.finfo(float).eps
        ),
    )

    rng = fwdpy11.GSLrng(simparams.fwdpy11_seed)
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
        / float(simparams.N)
    )[1]
    return afs, simparams


if __name__ == "__main__":
    parser = make_parser()
    args = parser.parse_args(sys.argv[1:])

    used_fp11_seeds = {}
    used_msprime_seeds = {}

    mean_afs = np.zeros(21)

    params = []

    for rho in np.linspace(MIN_RHO, MAX_RHO, args.num_recrates + 1):
        for alpha in np.linspace(MIN_ALPHA, MAX_ALPHA, args.num_recrates + 1):
            for i in range(args.nreps):
                msp_seed = np.random.randint(0, np.iinfo(np.uint32).max)
                while msp_seed in used_msprime_seeds:
                    msp_seed = np.random.randint(0, np.iinfo(np.uint32).max)
                used_msprime_seeds[msp_seed] = 1
                fp11_seed = np.random.randint(0, np.iinfo(np.uint32).max)
                while fp11_seed in used_fp11_seeds:
                    fp11_seed = np.random.randint(0, np.iinfo(np.uint32).max)
                params.append(
                    SimParams(
                        N=args.popsize,
                        rho=rho,
                        alpha=alpha,
                        msprime_seed=msp_seed,
                        fwdpy11_seed=fp11_seed,
                    )
                )

    if os.path.exists(DBNAME):
        os.remove(DBNAME)

    arrays = ForwardSimDataArrays()

    with concurrent.futures.ProcessPoolExecutor(max_workers=args.ncores) as executor:
        futures = {executor.submit(run_sim, i) for i in params}
        for future in concurrent.futures.as_completed(futures):
            afs, simparams = future.result()
            arrays.extend(afs, simparams)

            if arrays.len() > int(50e6):
                arrays.dump(DBNAME)

    if arrays.len() > 0:
        arrays.dump(DBNAME)
