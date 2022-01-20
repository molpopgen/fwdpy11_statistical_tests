import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import sqlite3
import sys

conn = sqlite3.connect(sys.argv[1])
output = sys.argv[2]

df = pd.read_sql("select * from windowed_variation", conn)

df = df.groupby(["window", "2Ns", "4Nr"]).mean().reset_index()

print(df.head())
print(df.tail())

g = sns.FacetGrid(df, row="2Ns", col="4Nr", margin_titles=True)
g.map(sns.scatterplot, "window", "diversity")

# g.set(xticks=np.arange(1, 20, 2))
g.set(xlabel="Window")
g.set(ylabel="Diversity (branch stat)")
g.add_legend()

plt.savefig(output)
