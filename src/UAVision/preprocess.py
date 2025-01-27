import pandas as pd
import numpy as np
import re
import json
import importlib.resources

mcda_midbin_all = (
    importlib.resources.files("UAVision").joinpath("mcda_midbin_all.txt").read_text()
)
mcda_midbin_all = json.loads(mcda_midbin_all)

pop_binedges = (
    importlib.resources.files("UAVision").joinpath("pops_binedges.txt").read_text()
)
pop_binedges = np.fromstring(pop_binedges, sep="\n")


def calculate_height(p0, p1, T0, T1):
    """Calculate height based on hydrostatic pressure equation, assuming a uniform layer"""
    R = 287.05
    g = 9.80665
    height = R / g * ((T0 + T1) / 2 + 273.15) * np.log(p0 / p1)
    return height


def calculate_height_df(df, p, T):
    """Advance calculation of height based on hydrostatic pressure equation, assuming mini uniform layer"""
    df_height = df.copy()
    df_height.dropna(subset=p, inplace=True)
    height = np.zeros_like(df_height[p])
    height[1:] = calculate_height(
        df_height[p][:-1].values,
        df_height[p][1:].values,
        df_height[T][:-1].values,
        df_height[T][1:].values,
    )
    df_height["height"] = height
    df["height"] = df_height["height"]
    df.replace({"height": np.nan}, 0, inplace=True)
    df["height"] = df["height"].cumsum()
    return df


def preprocess_bme(file):
    df = pd.read_csv(file)
    df = df.dropna(axis=0)
    df = df.reset_index(drop=True)
    df["datetime"] = pd.to_datetime(df["date"] + " " + df["time"])
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
    return df


def preprocess_cpc(file):
    df = pd.read_csv(file)
    df = df.dropna(axis=0)
    df = df.reset_index(drop=True)
    df["datetime"] = pd.to_datetime(df["date_time"])
    df = df.drop(["date_time"], axis=1)
    time_col = df.pop("datetime")
    df.insert(0, "datetime", time_col)
    df = df.rename(
        {"N conc(1/ccm)": "N_conc_cpc(1/ccm)", "Pressure (hPa)": "press_cpc (hPa)"},
        axis=1,
    )
    return df


def preprocess_mcda(file, size):
    """mCDA processing, calculate derived parameters as well"""
    # calculate size dlog_bin
    print(size)
    mid_bin = np.array(mcda_midbin_all[size], dtype=float)
    mid_bin = mid_bin[81:]
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
    df = df.iloc[:, np.r_[[0], 82:257, -6:0]]
    df = df.dropna(axis=0)
    df = df.reset_index(drop=True)
    df.columns = np.arange(df.columns.size)
    df[0] = pd.to_datetime(df[0], format="%Y%m%d%H%M%S")

    df_bins_label = ["bin" + str(x) + "_mcda (dN/dlogDp)" for x in range(1, 176)]
    df_pm_label = [
        "pcount_mcda",
        "pm1_mcda",
        "pm25_mcda",
        "pm4_mcda",
        "pm10_mcda",
        "pmtot_mcda",
    ]
    df.columns = np.r_[["datetime"], df_bins_label, df_pm_label]
    df.iloc[:, 1:-6] = df.iloc[:, 1:-6].map(
        lambda x: int(x, base=16)
    )  # Convert hex to int
    df = df.set_index("datetime").astype("float").reset_index()  # Convert to float
    # Bin counts
    df_bins = df.iloc[:, 1:176].copy().to_numpy().astype(float)
    # Calculate dN/dlogDp
    df.iloc[:, 1:176] = df.iloc[:, 1:176] / dlog_bin / 10 / 46.67
    # Calculate CDNC
    df["Nd_mcda (1/ccm)"] = df_bins.sum(axis=1) / 10 / 46.67
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
    df["ED_mcda (um)"] = 2 * np.divide(
        top, bottom, out=np.zeros_like(top), where=bottom != 0
    )
    # Drop columns
    df = df.drop(["pcount_mcda", "pm4_mcda", "pmtot_mcda"], axis=1)
    return df


def preprocess_pops(file):
    """POPS processing"""
    df = pd.read_csv(file)
    df = df.dropna(axis=0)
    df = df.reset_index(drop=True)
    df["datetime"] = pd.to_datetime(df["DateTime"], unit="s") + pd.Timedelta("2hour")
    df = df.set_index("datetime").resample("1s").mean().dropna().reset_index()
    df = df.drop(["DateTime"], axis=1)
    time_col = df.pop("datetime")
    df.insert(0, "datetime", time_col)

    dlog_bin = np.log10(pop_binedges[1:]) - np.log10(pop_binedges[:-1])
    pop_binlab = [
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

    for particle_size, each_dlog_bin in zip(pop_binlab, dlog_bin):
        df[particle_size] = (
            df[particle_size] / (df[" POPS_Flow"] * 16.6667) / each_dlog_bin
        )
    df.columns = [
        "bin" + str(int(x[1:]) + 1) + "_pops (dN/dlogDp)"
        if re.search("b[0-9]+", x)
        else x
        for x in df.columns
    ]

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
    )
    df = df.rename(
        {
            " PartCon": "N_conc_pops (1/ccm)",
            " P": "press_pops (hPa)",
            " POPS_Flow": "flow_rate_pops (l/m)",
        },
        axis=1,
    )
    return df


def calculate_binedges(midbin):
    """calculate bin edges for mcda mid bin"""
    binedges = np.append(
        np.append(
            midbin[0] - (-midbin[0] + midbin[1]) / 2, (midbin[:-1] + midbin[1:]) / 2
        ),
        (midbin[-1] - midbin[-2]) / 2 + midbin[-1],
    )
    return binedges


def calculate_midbin(pop_binedges):
    """calculate midbin for pop"""
    # pop_binedges = np.loadtxt('pops_binedges.txt')
    pop_midbin = (pop_binedges[1:] + pop_binedges[:-1]) / 2
    return pop_midbin


def cloudmask(df):
    """cloud mask for mcda"""
    if df["datetime"][0] < pd.Timestamp("20221003", tz="UTC"):
        size = "water_0.15-17"
    else:
        size = "water_0.6-40"
    cda_midbin = np.array(mcda_midbin_all[size], dtype=float)
    cda_midbin = cda_midbin[81:]
    binedges = calculate_binedges(cda_midbin)
    dlog_bin = np.log10(binedges[1:]) - np.log10(binedges[:-1])
    # RH > 80%
    rh_cloud = df["rh_bme (%)"] > 80
    # Count > 1 in 10s with size > 2 um
    bin_lab = [x for x in df.columns if "_mcda (dN/dlogDp)" in x]
    bin_lab_cloud = bin_lab[np.argmax(cda_midbin > 2) :]
    bin_count = df[bin_lab] * dlog_bin
    count_cloud = bin_count[bin_lab_cloud].sum(axis=1) * 10 > 5
    cloudmask = rh_cloud & count_cloud
    return cloudmask
