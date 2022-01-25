import argparse
import sys
import sqlite3
import dataframe_image
import pandas as pd


def make_parser():
    parser = argparse.ArgumentParser(
        description="Get the distribution of fixation times via naive simulation in Python.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument("--dbname", type=str, help="Name of sqlite3 database")
    parser.add_argument(
        "--pydbname",
        type=str,
        help="Name of sqlite3 database with Python fixation times",
    )

    return parser


parser = make_parser()
args = parser.parse_args(sys.argv[1:])


with sqlite3.connect(args.dbname) as conn:
    fp11 = pd.read_sql("select * from fwdpy11_fixation_times", conn)

with sqlite3.connect(args.pydbname) as conn:
    print(conn)
    print(args.pydbname)
    py = pd.read_sql("select * from python_fixation_times", conn)

fp11["simulator"] = ["fwdpy11"] * len(fp11.index)
py["simulator"] = ["python"] * len(py.index)

df = pd.concat([fp11, py])

df = df.groupby(["simulator", "alpha"]).describe()

dataframe_image.export(df, "output/fixation_times.png", table_conversion="matplotlib")
