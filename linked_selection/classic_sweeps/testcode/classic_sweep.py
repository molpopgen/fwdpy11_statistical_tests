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


ALPHAS = [100.0, 500.0, 1000.0, 2500.0]
RHOS = [10.0, 0.0, 90.0, 0.0, 900.0, 0.0]
LOCUS_LEN = 2000.0
SEQLEN = len(RHOS) * LOCUS_LEN
# L = 2000  # NOTE: may need/want a much larger value
LEFTS = np.arange(0, SEQLEN, LOCUS_LEN)
RIGHTS = LEFTS + LOCUS_LEN
WINDOWS = [i for i in LEFTS] + [SEQLEN]

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
        df = pd.DataFrame(
            {"eta": self.eta, "count": self.count, "2Ns": self.alpha, "4Nr": self.rho}
        )
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

    def extend(self, sfs, rho, simparams):
        n = len(sfs) - 2
        self.eta.extend([i + 1 for i in range(n)])
        self.alpha.extend([simparams.alpha] * n)
        self.rho.extend([rho] * n)
        self.count.extend(sfs[1:-1].tolist())


@dataclass
class SimParams:
    N: int
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

    return parser


def run_sim(simparams: SimParams):
    recregions = []
    position = []
    rate = []
    for left, right, rho in zip(LEFTS, RIGHTS, RHOS):
        recregions.append(
            fwdpy11.PoissonInterval(
                int(left), int(right), rho / 4 / simparams.N, discrete=True
            )
        )
        position.append(left)
        rate.append(rho / 4 / simparams.N / (right - left))
    position.append(SEQLEN)
    pdict = {
        "recregions": recregions,
        "nregions": [],
        "sregions": [],
        "gvalue": fwdpy11.Multiplicative(2.0),  # NOTE: scaling may be wrong
        "simlen": 100 * simparams.N,
        "rates": (0, 0, None),
    }

    params = fwdpy11.ModelParams(**pdict)

    recombination_rate = msprime.RateMap(position=position, rate=rate)
    ts = msprime.sim_ancestry(
        simparams.N,
        population_size=simparams.N,
        sequence_length=SEQLEN,
        recombination_rate=recombination_rate,
        random_seed=simparams.msprime_seed,
    )

    pop = fwdpy11.DiploidPopulation.create_from_tskit(ts)

    assert pop.N == simparams.N
    mutation_data = fwdpy11.conditional_models.NewMutationParameters(
        frequency=fwdpy11.conditional_models.AlleleCount(1),
        data=fwdpy11.NewMutationData(
            effect_size=simparams.alpha / 2 / pop.N, dominance=1
        ),
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
    ts2 = ts.simplify(samples=rsamples)  # .keep_intervals([[L // 2, L]])
    afs = (
        ts2.allele_frequency_spectrum(
            # sample_sets=[rsamples],
            mode="branch",
            span_normalise=True,
            polarised=True,
            windows=WINDOWS,
        )
        # normalize afs back down to a theta of 1.0
        / 4.0
        / float(simparams.N)
    )
    return afs, simparams


def dispatch_work(args):
    used_fp11_seeds = {}
    used_msprime_seeds = {}

    params = []

    for alpha in ALPHAS:
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
            i = 0
            cumrho = 0
            for rho, fs in zip(RHOS, afs):
                if rho == 0.0:
                    cumrho += RHOS[i - 1]
                    arrays.extend(fs, cumrho, simparams)
                i += 1

            if arrays.len() > int(50e6):
                arrays.dump(DBNAME)

    if arrays.len() > 0:
        arrays.dump(DBNAME)


if __name__ == "__main__":
    parser = make_parser()
    args = parser.parse_args(sys.argv[1:])

    dispatch_work(args)
