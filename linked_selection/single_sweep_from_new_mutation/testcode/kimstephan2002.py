"""
Equation 5 from Kim, Yuseob, and Wolfgang Stephan. 2002. “Detecting a Local Signature of Genetic Hitchhiking along a Recombining Chromosome.” Genetics 160 (2): 765–77.
"""

import argparse
import concurrent.futures
import math
from dataclasses import dataclass
import sqlite3
import sys

import numpy as np
import pandas as pd


@dataclass
class Record:
    alpha: float
    rho: float
    eta: float
    count: float


def phi1p(theta, p, r, s, epsilon):
    assert p > 0.0
    assert p < 1.0
    C = 1.0 - epsilon ** (r / s)

    if p < C:
        return theta / p - theta / C
    elif 1.0 - C < p:
        return theta / C
    return 0


def Pnk(n, k, theta, r, s, epsilon, delta):
    assert k > 0
    assert k < n
    p = delta
    rv = 0.0
    C = math.comb(n, k)
    ldelta = math.log(delta)
    while p < 1:
        # rv += p ** k * (1.0 - p) ** (n - k) * phi1p(theta, p, r, s, epsilon) * delta
        phi = phi1p(theta, p, r, s, epsilon)
        if phi > 0.0:
            temp = (
                k * math.log(p) + (n - k) * math.log(1.0 - p) + math.log(phi) + ldelta
            )
            rv += math.exp(temp)
        p += delta

    return C * rv


def polarised_sfs(N, rho, alpha, n, theta, delta=1e-5):
    r = rho / 4 / N
    s = alpha / 2 / N
    epsilon = 1.0 / alpha

    return alpha, rho, [Pnk(n, i, theta, r, s, epsilon, delta) for i in range(1, n)]


def make_parser():
    parser = argparse.ArgumentParser(
        description="Calculate the expected polarised SFS using approximations based on deterministic theory.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "--popsize", "-N", type=int, default=None, help="Diploid population size"
    )

    parser.add_argument(
        "--cores", "-c", type=int, default=1, help="Number of cores to use"
    )

    parser.add_argument("--dbname", type=str, help="Name of sqlite3 database")

    parser.add_argument(
        "--rhos",
        nargs="+",
        type=float,
        default=[],
        help="Cumulative scaled recombination rates (4Nr) from the selected mutation.",
    )

    parser.add_argument(
        "--alphas",
        nargs="+",
        type=float,
        default=[],
        help="Scaled selection coefficients (2Ns).",
    )

    parser.add_argument("--nsam", "-n", type=int, default=-1, help="Sample size.")

    return parser


parser = make_parser()
args = parser.parse_args(sys.argv[1:])

assert args.nsam >= 2

N = args.popsize

params = []

for rho in sorted(args.rhos):
    for alpha in args.alphas:
        params.append((rho, alpha))


data = []
with concurrent.futures.ProcessPoolExecutor(max_workers=args.cores) as executor:
    futures = {
        executor.submit(polarised_sfs, N, rho, alpha, args.nsam, 1.0, 1.0 / 50.0 / N)
        for rho, alpha in params
    }
    for future in concurrent.futures.as_completed(futures):
        alpha, rho, sfs = future.result()
        for i, c in enumerate(sfs):
            data.append(Record(alpha, rho, i + 1, c))

df = pd.DataFrame(data)

df = df.rename(columns={"rho": "4Nr", "alpha": "2Ns"})

with sqlite3.connect(args.dbname) as conn:
    df.to_sql("kimstephan", conn, index=False)
