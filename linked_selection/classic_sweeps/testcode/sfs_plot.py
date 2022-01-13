import pandas as pd
import matplotlib.pyplot as plt
import sqlite3
import sys

if __name__ == "__main__":
    print(sys.argv)
    for i, a in enumerate(sys.argv):
        print(i, a)
    conn = sqlite3.connect(sys.argv[1])
    output = sys.argv[2]
    df = pd.read_sql("select * from sfs", conn)

    df = df.groupby(["eta", "alpha"]).mean().reset_index()

    # print(df)
    # print(type(df))

    fig = plt.Figure()
    ax = fig.add_subplot()
    # print(df.eta)
    # print(df.count)
    plt.plot(df.eta, df["count"])

    # print(output)

    plt.savefig(output)
