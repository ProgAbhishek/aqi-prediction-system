import pandas as pd
import os


CSV_FILE = "../data/air_quality.csv"


def save_data(row):

    df = pd.DataFrame([row])

    if os.path.exists(CSV_FILE):

        df.to_csv(
            CSV_FILE,
            mode="a",
            index=False,
            header=False
        )

    else:

        df.to_csv(
            CSV_FILE,
            index=False
        )

    print("Data Saved Successfully.")