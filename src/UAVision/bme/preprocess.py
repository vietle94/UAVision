import pandas as pd
import numpy as np
from numpy.typing import NDArray
from os import PathLike


def calculate_height(
    p0: float | NDArray[np.float64],
    p1: float | NDArray[np.float64],
    T0: float | NDArray[np.float64],
    T1: float | NDArray[np.float64],
) -> float | NDArray[np.float64]:
    """
    Calculate height based on hydrostatic pressure equation, assuming a uniform layer

    p0: pressure at lower level (hPa)
    p1: pressure at upper level (hPa)
    T0: temperature at lower level (K)
    T1: temperature at upper level (K)
    """
    R = 287.05
    g = 9.80665
    height = R / g * ((T0 + T1) / 2 + 273.15) * np.log(p0 / p1)
    return height


def calculate_height_df(
    df: pd.DataFrame,
    p: str,
    T: str,
) -> pd.DataFrame:
    """
    Advance calculation of height based on hydrostatic pressure equation,
    assuming mini uniform layer
    df: dataframe containing pressure and temperature columns
    p: pressure column name (string) (hPa)
    T: temperature column name (string) (C)
    return: dataframe with height column added (meters)
    """
    df_height = df.copy()
    df_height.dropna(subset=p, inplace=True)
    height = np.zeros_like(df_height[p], dtype=np.float64)
    height[1:] = calculate_height(
        df_height[p][:-1].to_numpy(dtype=np.float64),
        df_height[p][1:].to_numpy(dtype=np.float64),
        df_height[T][:-1].to_numpy(dtype=np.float64),
        df_height[T][1:].to_numpy(dtype=np.float64),
    )
    df_height["height"] = height
    df["height"] = df_height["height"]
    df.replace({"height": np.nan}, 0, inplace=True)
    df["height"] = df["height"].cumsum()
    return df


def preprocess_bme(file: str | PathLike[str]) -> pd.DataFrame:
    """
    BME processing
    file: path to bme csv file (string or PathLike)
    return: processed dataframe
    """
    df = pd.read_csv(file)
    df = df.dropna(axis=0)
    df = df.reset_index(drop=True)
    df["datetime"] = pd.to_datetime(
        df["date"].astype(str) + " " + df["time"].astype(str)
    )
    df = df.drop(["date", "time"], axis=1)
    time_col = df.pop("datetime")
    df.insert(0, "datetime", time_col)
    df = df.rename(
        {
            "temp_bme": "temp_bme (C)",
            "press_bme": "press_bme (hPa)",
            "rh_bme": "rh_bme (%)",
        },
        axis=1,
    )
    df = calculate_height_df(df, "press_bme (hPa)", "temp_bme (C)")
    df = df.rename({"height": "height_bme (m)"}, axis=1)
    return df
