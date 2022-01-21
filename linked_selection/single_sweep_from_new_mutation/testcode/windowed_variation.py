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
    windowed_variation_model,
)


RHOS = [100.0, 1000.0]
DBNAME = "output/windowed_variation.sqlite3"


@dataclass
class ForwardSimDataArrays:
    # Arrays to store data
    window: List[int] = field(default_factory=list)
    div: List[int] = field(default_factory=list)
    alpha: List[float] = field(default_factory=list)
    rho: List[float] = field(default_factory=list)

    def len(self):
        return len(self.eta)

    def to_df(self):
        df = pd.DataFrame(
            {
                "window": self.window,
                "diversity": self.div,
                "2Ns": self.alpha,
                "4Nr": self.rho,
            }
        )
        return df

    def clear(self):
        self.window.clear()
        self.div.clear()
        self.alpha.clear()
        self.rho.clear()

    def dump(self, dbname):
        conn = sqlite3.connect(dbname)
        df = self.to_df()
        if len(df.index) > 0:
            df.to_sql("windowed_variation", conn, index=False, if_exists="append")
        self.clear()

    def extend(self, window, div, rho, simparams):
        self.window.append(window)
        self.div.append(div)
        self.alpha.append(simparams.alpha)
        self.rho.append(rho)


@dataclass
class SimParams:
    alpha: float
    fwdpy11_seed: int


def make_parser():
    parser = argparse.ArgumentParser(
        description=" ",
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
        "--num_windows", "-w", type=int, default=1000, help="Number of windows"
    )

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
                left=setup.seqlen / 2.0,
                right=setup.seqlen / 2.0 + 1,
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
        div = (
            ts2.diversity(
                mode="branch",
                span_normalise=True,
                windows=setup.windows,
            )
            # normalize afs back down to a theta of 1.0
            # / 4.0
            # / float(setup.N)
        )
        for i, a in enumerate(div):
            arrays.extend(i, a, 4 * params.recregions[0].mean * setup.N, mparams)
    return arrays


def dispatch_work(args):
    used_fp11_seeds = {}
    used_msprime_seeds = {}

    params = []
    msprime_seeds = []
    setups = []

    initial_setups = [
        windowed_variation_model(args.popsize, rho, args.num_windows) for rho in RHOS
    ]

    for _ in range(args.ncores):
        for setup in initial_setups:
            for alpha in setup.alphas:
                msp_seed = np.random.randint(0, np.iinfo(np.uint32).max)
                while msp_seed in used_msprime_seeds:
                    msp_seed = np.random.randint(0, np.iinfo(np.uint32).max)
                used_msprime_seeds[msp_seed] = 1
                msprime_seeds.append(msp_seed)
    for _ in range(args.nreps):
        for setup in initial_setups:
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
                setups.append(setup)

    if os.path.exists(DBNAME):
        os.remove(DBNAME)

    with concurrent.futures.ProcessPoolExecutor(max_workers=args.ncores) as executor:
        futures = {
            executor.submit(run_sim, setup, i, j)
            for setup, i, j in zip(
                setups,
                np.array_split(params, args.ncores),
                msprime_seeds,
            )
        }
        for future in concurrent.futures.as_completed(futures):
            arrays = future.result()
            arrays.dump(DBNAME)


if __name__ == "__main__":
    parser = make_parser()
    args = parser.parse_args(sys.argv[1:])

    dispatch_work(args)
