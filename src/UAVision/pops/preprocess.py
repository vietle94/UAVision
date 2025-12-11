import pandas as pd
import numpy as np
import importlib.resources

pops_binedges = (
    importlib.resources.files("UAVision.bin_edges").joinpath("pops_binedges.txt").read_text()
)
pops_binedges = np.fromstring(pops_binedges, sep="\n")

def preprocess_pops(file, size=None, drop_aux=True):
    """
    POPS processing

    file: path to pops csv file (string)
    size: optional. If None uses bundled pops_binedges (bin edges).
          If array-like is provided it must be the bin edges with length 17.
    drop_aux: bool, if True drop auxiliary columns (default True). If False keep them.
    return: processed dataframe
    """
    df = pd.read_csv(file)
    df = df.dropna(axis=0)
    df = df.reset_index(drop=True)
    df["datetime"] = pd.to_datetime(df["DateTime"], unit="s")
    df = df.set_index("datetime").resample("1s").mean().dropna().reset_index()
    df = df.drop(["DateTime"], axis=1)
    time_col = df.pop("datetime")
    df.insert(0, "datetime", time_col)

    # determine binedges from provided size or bundled pops_binedges
    if size is None:
        binedges = pops_binedges.astype(float)
    elif isinstance(size, (list, tuple, np.ndarray, pd.Series)):
        arr = np.asarray(size, dtype=float)
        if arr.ndim != 1 or arr.size != 17:
            raise ValueError("When providing 'size' as an array it must be a 1-D array of 17 bin edges.")
        binedges = arr
    else:
        raise TypeError("size must be None or an array-like of 17 bin edges")

    dlog_bin = np.log10(binedges[1:]) - np.log10(binedges[:-1])

    pops_binlab = [
        "b0",
        "b1",
        "b2",
        "b3",
        "b4",
        "b5",
        "b6",
        "b7",
        "b8",
        "b9",
        "b10",
        "b11",
        "b12",
        "b13",
        "b14",
        "b15",
    ]
    dndlog_label = ["bin" + str(x) + "_pops (dN/dlogDp)" for x in range(1, 17)]
    conc_label = ["bin" + str(x) + "_pops (cm-3)" for x in range(1, 17)]
    df = df.rename(columns={x:y for x,y in zip(pops_binlab, conc_label)})
    # Calculate concentration cm-3
    df[conc_label] = df[conc_label].div(df[" POPS_Flow"] * 16.6667, axis=0)
    # Calculate dN/dlogDp
    dndlog = df[conc_label].div(dlog_bin, axis=1)
    dndlog.columns = dndlog_label
    df = pd.concat([df, dndlog], axis=1)
        
    if drop_aux:
        df = df.drop(
            [
                " Status",
                " PartCt",
                " BL",
                " BLTH",
                " STD",
                " TofP",
                " PumpFB",
                " LDTemp",
                " LaserFB",
                " LD_Mon",
                " Temp",
                " BatV",
                " Laser_Current",
                " Flow_Set",
                "PumpLife_hrs",
                " BL_Start",
                " TH_Mult",
                " nbins",
                " logmin",
                " logmax",
                " Skip_Save",
                " MinPeakPts",
                "MaxPeakPts",
                " RawPts",
            ],
            axis=1,
            errors="ignore",
        )
    df = df.rename(
        {
            " PartCon": "N_conc_pops (cm-3)",
            " P": "press_pops (hPa)",
            " POPS_Flow": "flow_rate_pops (l/m)",
        },
        axis=1,
    )
    return df