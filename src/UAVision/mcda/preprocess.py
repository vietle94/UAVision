import importlib.resources
import json
import numpy as np
import pandas as pd

mcda_midbin_all = (
    importlib.resources.files("UAVision.bin_edges").joinpath("mcda_midbin_all.txt").read_text()
)
mcda_midbin_all = json.loads(mcda_midbin_all)


def preprocess_mcda(file, size):
    """
    mCDA processing, calculate derived parameters as well
    file: path to mcda csv file (string)
    size: size category string, one of the following
      ['PSL_0.6-40', 'PSL_0.15-17', 'water_0.6-40', 'water_0.15-17'] OR
      an array-like of mid-bin values (list/tuple/ndarray)
      If an array-like is provided, it must be length 256.
    return: processed dataframe
    """
    # accept an array-like of mid_bin values as well as a size key string
    if isinstance(size, (list, tuple, np.ndarray, pd.Series)):
        mid_bin = np.asarray(size, dtype=float)
        if mid_bin.ndim != 1 or mid_bin.size != 256:
            raise ValueError(
                "When providing an array-like 'size', it must be one-dimensional with length 256."
            )
    elif isinstance(size, str):
        if size not in mcda_midbin_all:
            raise KeyError(
                f"size '{size}' not found. Valid keys: {list(mcda_midbin_all.keys())}"
            )
        mid_bin = np.array(mcda_midbin_all[size], dtype=float)
    else:
        raise TypeError("size must be a key string or an array-like of 256 mid-bin values")

    # calculate size dlog_bin
    print(size)
    binedges = np.append(
        np.append(
            mid_bin[0] - (-mid_bin[0] + mid_bin[1]) / 2,
            (mid_bin[:-1] + mid_bin[1:]) / 2,
        ),
        (mid_bin[-1] - mid_bin[-2]) / 2 + mid_bin[-1],
    )
    dlog_bin = np.log10(binedges[1:]) - np.log10(binedges[:-1])

    # Load file
    df = pd.read_csv(file, skiprows=1, header=None, dtype=str)
    df = df.iloc[:, np.r_[0:257, -6:0]]
    df = df.dropna(axis=0)
    df = df.reset_index(drop=True)
    df.columns = np.arange(df.columns.size)
    df[0] = pd.to_datetime(df[0], format="%Y%m%d%H%M%S")

    dndlog_label = ["bin" + str(x) + "_mcda (dN/dlogDp)" for x in range(1, 257)]
    conc_label = ["bin" + str(x) + "_mcda (cm-3)" for x in range(1, 257)]
    pm_label = [
        "pcount_mcda",
        "pm1_mcda",
        "pm25_mcda",
        "pm4_mcda",
        "pm10_mcda",
        "pmtot_mcda",
    ]
    df.columns = np.r_[["datetime"], conc_label, pm_label]

    # Convert hex to int
    df[conc_label] = df[conc_label].map(
        lambda x: int(x, base=16)
    )
    # Convert to float
    df = df.set_index("datetime").astype("float").reset_index() 
    # Bin counts
    df_bins = df[conc_label].copy().to_numpy().astype(float)
    # Calculate concentration cm-3
    df[conc_label] = df[conc_label] / 10 / 46.67  # 10s averaged, 2.8L/min flow = 46.67 ccm/s

    # Calculate dN/dlogDp
    dndlog = df[conc_label] / dlog_bin
    dndlog.columns = dndlog_label
    df = pd.concat([df, dndlog], axis=1)    
    # Calculate CDNC
    df["Nd_mcda (cm-3)"] = df_bins.sum(axis=1) / 10 / 46.67
    # Calculate LWC
    conc_perbin = df_bins / 10 / (2.8e-3 / 60)
    lwc_perbin = conc_perbin * 1e6 * np.pi / 6 * (mid_bin * 1e-6) ** 3
    lwc_sum = lwc_perbin.sum(axis=1)
    df["LWC_mcda (g/m3)"] = lwc_sum
    # Calculate MVD
    p_lwc_perbin = np.divide(
        lwc_perbin,
        lwc_sum[:, np.newaxis],
        out=np.zeros_like(lwc_perbin),
        where=lwc_sum[:, np.newaxis] != 0,
    )
    cumsum_lwc_perbin = p_lwc_perbin.cumsum(axis=1)
    cumsum_lwc_perbin[df_bins == 0] = np.nan
    # find imin and imax, they contain the point where cumsum_lwc_perbin == 0.5
    imax = np.argmax((cumsum_lwc_perbin > 0.5), axis=1)
    imin = (
        cumsum_lwc_perbin.shape[1]
        - np.argmax(cumsum_lwc_perbin[:, ::-1] < 0.5, axis=1)
        - 1
    )
    # The MVD formula is based on this where max is first non-zero bin cumsum > 0.5 and
    # min is last non-zero bin cumsum < 0.5
    # (0.5 - cum_min) / (cum_max - cum_min) = (bx - bmin) / (bmax - bmin)
    cum_min = cumsum_lwc_perbin[np.arange(len(cumsum_lwc_perbin)), imin]
    cum_max = cumsum_lwc_perbin[np.arange(len(cumsum_lwc_perbin)), imax]
    bmin = mid_bin[imin]
    bmax = mid_bin[imax]
    df["MVD_mcda (um)"] = bmin + (0.5 - cum_min) / (cum_max - cum_min) * (bmax - bmin)
    # Calculate ED
    top = (conc_perbin * mid_bin**3).sum(axis=1)
    bottom = (conc_perbin * mid_bin**2).sum(axis=1)
    df["ED_mcda (um)"] = np.divide(
        top, bottom, out=np.zeros_like(top), where=bottom != 0
    )
    # Drop columns
    df = df.drop(["pcount_mcda", "pm4_mcda", "pmtot_mcda"], axis=1)
    return df


def cloudmask(df):
    import re
    """cloud mask for mcda"""
    if df["datetime"][0] < pd.Timestamp("20221003"):
        size = "water_0.15-17"
    else:
        size = "water_0.6-40"
    cda_midbin = np.array(mcda_midbin_all[size], dtype=float)
    cda_midbin = cda_midbin[81:]
    # RH > 80%
    rh_cloud = df["rh_bme (%)"] > 80
    # Count > 1 in 10s with size > 2 um
    bin_lab = [x for x in df.columns if re.search(r"bin[0-9]+_mcda \(cm-3\)", x)]
    bin_lab_cloud = bin_lab[np.argmax(cda_midbin > 2) :]
    bin_count = df[bin_lab]
    count_cloud = bin_count[bin_lab_cloud].sum(axis=1) * 10 > 5
    cloudmask = rh_cloud & count_cloud
    return cloudmask
