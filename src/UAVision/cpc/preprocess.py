import pandas as pd
import numpy as np


def preprocess_cpc(file):
    """
    CPC processing
    file: path to cpc csv file (string)
    return: processed dataframe
    """
    df = pd.read_csv(file)
    df = df.dropna(axis=0)
    df = df.reset_index(drop=True)
    df["datetime"] = pd.to_datetime(df["date_time"])
    df.replace(0, np.nan, inplace=True) # 0 values are invalid
    df = df.drop(["date_time"], axis=1)
    time_col = df.pop("datetime")
    df.insert(0, "datetime", time_col)
    df = df.rename(
        {"N conc(1/ccm)": "N_conc_cpc (cm-3)", "Pressure (hPa)": "press_cpc (hPa)"},
        axis=1,
    )
    return df
