import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import sqlite3
import sys

conn = sqlite3.connect(sys.argv[1])
output = sys.argv[2]

# This script will take up
# too much RAM if we load then aggregate.
df = pd.read_sql(
    'select "2Ns","4Nr",window,avg(diversity) as diversity from windowed_variation group by "2Ns", "4Nr", window',
    conn,
)

# df = df.groupby(["window", "2Ns", "4Nr"]).mean().reset_index()

g = sns.FacetGrid(df, row="2Ns", col="4Nr", margin_titles=True)
g.map(sns.scatterplot, "window", "diversity")

# g.set(xticks=np.arange(1, 20, 2))
g.set(xlabel="Window")
g.set(ylabel="Diversity (branch stat)")
g.add_legend()

plt.savefig(output)
