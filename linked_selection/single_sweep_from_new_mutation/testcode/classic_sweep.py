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

from testutils import (
    SimulationSetup,
    main_sfs_figure_model,
)


@dataclass
class FixationTime:
    alpha: float
    fixation_time: int


@dataclass
class ForwardSimDataArrays:
    # Arrays to store data
    eta: List[int] = field(default_factory=list)
    count: List[float] = field(default_factory=list)
    alpha: List[float] = field(default_factory=list)
    rho: List[float] = field(default_factory=list)
    fixation_times: List[FixationTime] = field(default_factory=list)

    def len(self):
        return len(self.eta)

    def to_df(self):
        df = pd.DataFrame(
            {
                "eta": self.eta,
                "count": self.count,
                "2Ns": self.alpha,
                "4Nr": self.rho,
            }
        )
        fdf = pd.DataFrame(self.fixation_times)
        return df, fdf

    def clear(self):
        self.eta.clear()
        self.count.clear()
        self.alpha.clear()
        self.rho.clear()
        self.fixation_times.clear()

    def dump(self, dbname):
        conn = sqlite3.connect(dbname)
        df, fdf = self.to_df()
        if len(df.index) > 0:
            df.to_sql("sfs", conn, index=False, if_exists="append")
            fdf.to_sql("fwdpy11_fixation_times", conn, index=False, if_exists="append")
        self.clear()

    def extend(self, sfs, rho, simparams):
        n = len(sfs) - 2
        self.eta.extend([i + 1 for i in range(n)])
        self.alpha.extend([simparams.alpha] * n)
        self.rho.extend([rho] * n)
        self.count.extend(sfs[1:-1].tolist())

    def append_fixation_time(self, pop, simparams):
        assert len(pop.fixation_times) == 1
        self.fixation_times.append(FixationTime(simparams.alpha, pop.fixation_times[0]))


@dataclass
class SimParams:
    alpha: float
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

    parser.add_argument("--dbname", type=str, help="Name of sqlite3 database")

    return parser


def run_sim(setup: SimulationSetup, modelparams: List[SimParams], msprime_seed):
    arrays = ForwardSimDataArrays()

    for ts, mparams in zip(
        msprime.sim_ancestry(
            num_replicates=len(modelparams),
            random_seed=msprime_seed,
            **setup.sim_ancestry_kwargs,
        ),
        modelparams,
    ):
        pop = fwdpy11.DiploidPopulation.create_from_tskit(ts)
        assert pop.N == setup.N
        params = fwdpy11.ModelParams(**setup.pdict)
        mutation_data = fwdpy11.conditional_models.NewMutationParameters(
            frequency=fwdpy11.conditional_models.AlleleCount(1),
            data=fwdpy11.NewMutationData(
                effect_size=mparams.alpha / 2 / pop.N,
                dominance=setup.dominance,
            ),
            position=fwdpy11.conditional_models.PositionRange(
                left=0.0, right=np.finfo(float).eps
            ),
        )

        rng = fwdpy11.GSLrng(mparams.fwdpy11_seed)
        output = fwdpy11.conditional_models.selective_sweep(
            rng,
            pop,
            params,
            mutation_data,
            fwdpy11.conditional_models.GlobalFixation(),
            return_when_stopping_condition_met=True,
        )
        ts = output.pop.dump_tables_to_tskit()
        rsamples = np.sort(
            np.random.choice([i for i in ts.samples()], 20, replace=False)
        )
        ts2 = ts.simplify(samples=rsamples)  # .keep_intervals([[L // 2, L]])
        afs = (
            ts2.allele_frequency_spectrum(
                mode="branch",
                span_normalise=True,
                polarised=True,
                windows=setup.windows,
            )
            # normalize afs back down to a theta of 1.0
            / 4.0
            / float(setup.N)
        )
        cumrho = 0
        for rho, fs in zip(setup.rhos[0::2], afs[1::2]):
            cumrho += rho
            arrays.extend(fs, cumrho, mparams)
        arrays.append_fixation_time(output.pop, mparams)
    return arrays


def dispatch_work(args):
    used_fp11_seeds = {}
    used_msprime_seeds = {}

    params = []
    msprime_seeds = []

    setup = main_sfs_figure_model(args.popsize)

    for _ in range(args.ncores):
        for alpha in setup.alphas:
            msp_seed = np.random.randint(0, np.iinfo(np.uint32).max)
            while msp_seed in used_msprime_seeds:
                msp_seed = np.random.randint(0, np.iinfo(np.uint32).max)
            used_msprime_seeds[msp_seed] = 1
            msprime_seeds.append(msp_seed)
    for _ in range(args.nreps):
        for alpha in setup.alphas:
            fp11_seed = np.random.randint(0, np.iinfo(np.uint32).max)
            while fp11_seed in used_fp11_seeds:
                fp11_seed = np.random.randint(0, np.iinfo(np.uint32).max)
            params.append(
                SimParams(
                    alpha=alpha,
                    fwdpy11_seed=fp11_seed,
                )
            )

    if os.path.exists(args.dbname):
        os.remove(args.dbname)

    with concurrent.futures.ProcessPoolExecutor(max_workers=args.ncores) as executor:
        futures = {
            executor.submit(run_sim, setup, i, j)
            for i, j in zip(
                np.array_split(params, args.ncores),
                msprime_seeds,
            )
        }
        for future in concurrent.futures.as_completed(futures):
            arrays = future.result()
            arrays.dump(args.dbname)


if __name__ == "__main__":
    parser = make_parser()
    args = parser.parse_args(sys.argv[1:])

    dispatch_work(args)
