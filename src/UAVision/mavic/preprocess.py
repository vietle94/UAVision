import numpy as np
import importlib.resources
import pandas as pd

n2_binedges = (
    importlib.resources.files("UAVision.mavic")
    .joinpath("opcN2_binedges.txt")
    .read_text()
)
n2_binedges = np.fromstring(n2_binedges, sep="\n")

n3_binedges = (
    importlib.resources.files("UAVision.mavic")
    .joinpath("opcN3_binedges.txt")
    .read_text()
)
n3_binedges = np.fromstring(n3_binedges, sep="\n")


def calculate_concentration(df, bin_label, flow_label=None, period_label=None):
    """Calculate dN/dLogDp from OPC N2 and N3"""
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

def calculate_lag(df, var1, var2, lag):
    """Calculate the lag between two variables, same dataframe.
    Please resample the dataframe so spacing is consistent"""
    lag_range = np.arange(-lag, lag+1)
    df_corr = pd.DataFrame({
        'covariance': np.array([df[var1].corr(df[var2].shift(x)) for x in lag_range]),
        'lag': lag_range})
    df_corr['covariance'] = df_corr['covariance'].abs()
    imax = df_corr['covariance'].idxmax()
    lag_max = df_corr['lag'][imax]
    print(f"Max correlation when shift forward {var2} by {lag_max} seconds")
    return lag_max