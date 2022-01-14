import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import sqlite3
import sys

if __name__ == "__main__":
    print(sys.argv)
    for i, a in enumerate(sys.argv):
        print(i, a)
    conn = sqlite3.connect(sys.argv[1])
    output = sys.argv[2]
    df = pd.read_sql("select * from sfs", conn)

    df = df.groupby(["eta", "2Ns", "4Nr"]).mean().reset_index()

    g = sns.FacetGrid(df, row="2Ns", col="4Nr", margin_titles=True)
    g.map(sns.scatterplot, "eta", "count")

    g.set(xticks=np.arange(1, 20, 2))
    g.set(xlabel=r"$\eta$")
    g.set(ylabel="E[# mutations]")

    plt.savefig(output)
