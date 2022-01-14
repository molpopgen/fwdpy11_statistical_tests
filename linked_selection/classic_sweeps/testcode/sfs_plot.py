import pandas as pd
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

    df = df.groupby(["eta", "alpha", "rho"]).mean().reset_index()

    g = sns.FacetGrid(df, row="alpha", col="rho", margin_titles=True)
    g.map(sns.scatterplot, "eta", "count")

    plt.savefig(output)
