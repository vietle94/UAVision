from __future__ import annotations
import numpy as np
from numpy.typing import NDArray
import importlib.resources
import pandas as pd
from typing import Sequence

n2_binedges: NDArray[np.float64] = np.fromstring(
    importlib.resources.files("UAVision.bin_edges")
    .joinpath("opcN2_binedges.txt")
    .read_text(),
    sep="\n",
)

n3_binedges: NDArray[np.float64] = np.fromstring(
    importlib.resources.files("UAVision.bin_edges")
    .joinpath("opcN3_binedges.txt")
    .read_text(),
    sep="\n",
)


def calculate_concentration(
    df: pd.DataFrame,
    bin_label: Sequence[str],
    flow_label: str | None = None,
    period_label: str | None = None,
) -> pd.DataFrame | tuple[pd.DataFrame, pd.DataFrame]:
    """
    Calculate dN/dLogDp from OPC N2 and N3
    df: dataframe containing bin counts and flow rate
    bin_label: list of bin column names (string)
    flow_label: flow rate column name (string), only for OPC N3
    period_label: sampling period column name (string), only for OPC N3
    return: dN/dLogDp dataframe for OPC N2
            concentration and dN/dLogDp dataframe for OPC N3
    """
    if len(bin_label) == 16:
        print("OPC-N2")
        dlog_bin = np.log10(n2_binedges[1:]) - np.log10(n2_binedges[:-1])
        dndlogdp = df[bin_label].div(dlog_bin, axis=1)
        return dndlogdp

    elif len(bin_label) == 24:
        print("OPC-N3")
        dlog_bin = np.log10(n3_binedges[1:]) - np.log10(n3_binedges[:-1])
        total_volume = df[flow_label] / 100
        period = df[period_label] / 100
        concentration = df[bin_label].div(total_volume, axis=0).div(period, axis=0)
        dndlogdp = concentration.div(dlog_bin, axis=1)
        return concentration, dndlogdp

    else:
        raise ValueError(
            f"bin_label must have 16 (OPC-N2) or 24 (OPC-N3) columns, got {len(bin_label)}"
        )


def calculate_lag(df: pd.DataFrame, var1: str, var2: str, lag: int) -> int:
    """
    Calculate the lag between two variables, same dataframe.
    Please resample the dataframe so spacing is consistent
    df: dataframe containing the two variables
    var1: first variable column name (string)
    var2: second variable column name (string)
    lag: maximum lag to consider (int)
    return: lag value at maximum correlation (int)
    """
    lag_range = np.arange(-lag, lag + 1)
    df_corr = pd.DataFrame(
        {
            "covariance": np.array(
                [df[var1].corr(df[var2].shift(int(x))) for x in lag_range]
            ),
            "lag": lag_range,
        }
    )
    df_corr["covariance"] = df_corr["covariance"].abs()
    imax = df_corr["covariance"].idxmax()
    lag_max = df_corr["lag"][imax]
    print(f"Max correlation when shift forward {var2} by {lag_max} units")
    return lag_max
