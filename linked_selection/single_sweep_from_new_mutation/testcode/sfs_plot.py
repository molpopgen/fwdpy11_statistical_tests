import argparse
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import sqlite3
import sys


def make_parser():
    parser = argparse.ArgumentParser(
        description="Get the distribution of fixation times via naive simulation in Python.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument("--dbname", type=str, help="Name of sqlite3 database")
    parser.add_argument(
        "--ksdbname", type=str, help="Name of Kim/Stephan sqlite3 database"
    )

    parser.add_argument("--outfile", type=str, help="Output file name (png)")

    return parser


if __name__ == "__main__":
    parser = make_parser()
    args = parser.parse_args(sys.argv[1:])
    conn = sqlite3.connect(args.dbname)
    ksconn = sqlite3.connect(args.ksdbname)

    df = pd.read_sql("select * from sfs", conn)

    df = df.groupby(["eta", "2Ns", "4Nr"]).mean().reset_index()

    ks = pd.read_sql("select * from kimstephan", ksconn)

    df["source"] = ["fwdpy11"] * len(df.index)
    ks["source"] = ["theory"] * len(ks.index)

    df = pd.concat([df, ks])

    g = sns.FacetGrid(df, row="2Ns", col="4Nr", hue="source", margin_titles=True)
    g.map(sns.scatterplot, "eta", "count", alpha=0.75)

    g.set(xticks=np.arange(1, 20, 2))
    g.set(xlabel=r"$\eta$")
    g.set(ylabel="E[# mutations]")
    g.add_legend()

    plt.savefig(args.outfile)
