import sqlite3
import dataframe_image
import pandas as pd

from testutils import DBNAME

with sqlite3.connect(DBNAME) as conn:
    fp11 = pd.read_sql("select * from fwdpy11_fixation_times", conn)
    py = pd.read_sql("select * from python_fixation_times", conn)

    fp11["simulator"] = ["fwdpy11"] * len(fp11.index)
    py["simulator"] = ["python"] * len(py.index)

    df = pd.concat([fp11, py])

    df = df.groupby(["simulator", "alpha"]).describe()

    dataframe_image.export(
        df, "output/fixation_times.png", table_conversion="matplotlib"
    )
