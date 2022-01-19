import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import sqlite3
import sys

if __name__ == "__main__":
    conn = sqlite3.connect(sys.argv[1])
    output = sys.argv[2]

    df = pd.read_sql("select * from sfs", conn)

    df = df.groupby(["eta", "2Ns", "4Nr"]).mean().reset_index()

    ks = pd.read_sql("select * from kimstephan", conn)

    df["source"] = ["fwdpy11"] * len(df.index)
    ks["source"] = ["theory"] * len(ks.index)

    df = pd.concat([df, ks])

    g = sns.FacetGrid(df, row="2Ns", col="4Nr", hue="source", margin_titles=True)
    g.map(sns.scatterplot, "eta", "count", alpha=0.75)

    g.set(xticks=np.arange(1, 20, 2))
    g.set(xlabel=r"$\eta$")
    g.set(ylabel="E[# mutations]")
    g.add_legend()

    plt.savefig(output)
