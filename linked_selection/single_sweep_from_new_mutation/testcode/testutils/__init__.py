from dataclasses import dataclass
from typing import List, Dict
import fwdpy11
import msprime
import numpy as np


ALPHAS = [100.0, 1000.0, 10000.0]
CUM_RHOS = [10.0, 100.0, 1000.0]
RHOS = []
__last_rho = 0
for i in CUM_RHOS:
    RHOS.append(i - __last_rho)
    __last_rho += RHOS[-1]
    RHOS.append(0.0)
LOCUS_LEN = 1e6
SEQLEN = len(RHOS) * LOCUS_LEN
LEFTS = np.arange(0, SEQLEN, LOCUS_LEN)
RIGHTS = LEFTS + LOCUS_LEN
WINDOWS = [i for i in LEFTS] + [SEQLEN]
DBNAME = "output/data.sqlite3"

SCALING = 2.0
DOMINANCE = 1.0

KIM_STEPAN_FIG4_N = int(2e5)
KIM_STEPAN_FIG4_S = 1e-3
KIM_STEPAN_FIG4_R_OVER_S = [0.01, 0.1, 0.2]
KIM_STEPAN_FIG4_R = [i * KIM_STEPAN_FIG4_S for i in KIM_STEPAN_FIG4_R_OVER_S]


@dataclass
class SimulationSetup:
    N: int
    seqlen: float
    dominance: float
    scaling: float
    rhos: List[float]
    alphas: List[float]
    windows: List[float]
    pdict: Dict
    sim_ancestry_kwargs: Dict


def main_sfs_figure_model(N) -> SimulationSetup:
    recregions = []
    position = []
    rate = []
    for left, right, rho in zip(LEFTS, RIGHTS, RHOS):
        recregions.append(
            fwdpy11.PoissonInterval(int(left), int(right), rho / 4 / N, discrete=True)
        )
        position.append(left)
        rate.append(rho / 4 / N / (right - left))
    position.append(SEQLEN)
    pdict = {
        "recregions": recregions,
        "nregions": [],
        "sregions": [],
        "gvalue": fwdpy11.Multiplicative(SCALING),
        "simlen": 100 * N,
        "rates": (0, 0, None),
    }
    recombination_rate = msprime.RateMap(position=position, rate=rate)

    sim_ancestry_kwargs = {
        "samples": N,
        "population_size": N,
        "sequence_length": SEQLEN,
        "recombination_rate": recombination_rate,
    }

    return SimulationSetup(
        N, SEQLEN, DOMINANCE, SCALING, RHOS, ALPHAS, WINDOWS, pdict, sim_ancestry_kwargs
    )


def windowed_variation_model(N, rho, num_windows) -> SimulationSetup:
    L = 1e6

    recregions = [fwdpy11.PoissonInterval(0, int(L), rho / 4 / N, discrete=True)]
    pdict = {
        "recregions": recregions,
        "nregions": [],
        "sregions": [],
        "gvalue": fwdpy11.Multiplicative(SCALING),
        "simlen": 100 * N,
        "rates": (0, 0, None),
    }
    recombination_rate = msprime.RateMap(position=[0.0, L], rate=[rho / 4 / N / L])
    sim_ancestry_kwargs = {
        "samples": N,
        "population_size": N,
        "sequence_length": L,
        "recombination_rate": recombination_rate,
    }

    windows = np.arange(0, L, num_windows).tolist() + [L]
    return SimulationSetup(
        N, L, DOMINANCE, SCALING, [rho], ALPHAS, windows, pdict, sim_ancestry_kwargs
    )
