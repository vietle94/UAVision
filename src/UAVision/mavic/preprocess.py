import numpy as np
import importlib.resources

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


def calculate_dlogbin(df, bin_label, flow_label=None, period_label=None):
    """Calculate dN/dLogDp from OPC N2 and N3"""
    if len(bin_label) == 16:
        print("OPC-N2")
        dlog_bin = np.log10(n2_binedges[1:]) - np.log10(n2_binedges[:-1])
        total_concentration = df[bin_label].sum(axis=1)
        dndlogdp = df[bin_label].div(dlog_bin, axis=1)
        return dndlogdp, total_concentration

    elif len(bin_label) == 24:
        print("OPC-N3")
        dlog_bin = np.log10(n3_binedges[1:]) - np.log10(n3_binedges[:-1])
        total_volume = df[flow_label] / 100
        period = df[period_label] / 100
        concentration = df[bin_label].div(total_volume, axis=0).div(period, axis=0)
        total_concentration = concentration.sum(axis=1)
        dndlogdp = concentration.div(dlog_bin, axis=1)
        return dndlogdp, total_concentration
