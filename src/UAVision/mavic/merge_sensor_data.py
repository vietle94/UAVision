import pandas as pd
import glob
import os
import re
from functools import reduce
import argparse


def merge_sensor_data(dir_in, dir_out):
    dir_in = dir_in.replace("\\", "/") + "/"
    dir_out = dir_out.replace("\\", "/") + "/"

    sub_dir = [f.path for f in os.scandir(dir_in) if f.is_dir()]
    file_types = [".csv", ".txt"]
    for sub_dir_ in sub_dir:
        file_path = []
        for file_type in file_types:
            file_path.extend([x for x in glob.glob(sub_dir_ + "/*" + file_type)])
        file_name = [os.path.basename(x).rsplit(".", 1)[0] for x in file_path]
        instrument_name = [re.sub(r"[\.\-_][0-9]+", "", x) for x in file_name]
        file_summary = pd.DataFrame(
            {
                "file_path": file_path,
                "file_name": file_name,
                "instrument_name": instrument_name,
            }
        )
        data = {}
        for instrument, grp in file_summary.groupby("instrument_name"):
            data[instrument] = pd.concat(
                [
                    pd.read_csv(
                        x,
                        index_col=False,
                        sep=pd.read_csv(
                            x, sep=None, iterator=True, nrows=2
                        )._engine.data.dialect.delimiter,
                    )
                    for x in grp.file_path
                ],
                ignore_index=True,
            )

        for key, val in data.items():
            data[key] = data[key].dropna(axis=0, how="all")
            data[key].columns = data[key].columns.str.replace(" ", "")
            if "datetime" in data[key].columns:
                data[key]["datetime"] = pd.to_datetime(data[key]["datetime"])
            else:
                if "time" not in data[key].columns:
                    data[key]["datetime"] = pd.to_datetime(data[key]["date"])
                    data[key].drop(["date"], axis=1, inplace=True)
                else:
                    data[key]["datetime"] = pd.to_datetime(
                        data[key]["date"] + " " + data[key]["time"]
                    )
                    data[key].drop(["date", "time"], axis=1, inplace=True)
            data[key]["datetime"] = data[key]["datetime"].dt.floor("1s")
            data[key].columns = [
                x + "_" + key if "datetime" not in x else x for x in data[key].columns
            ]

        data_merged = reduce(
            lambda left, right: pd.merge(left, right, on=["datetime"], how="outer"),
            data.values(),
        )
        data_merged = data_merged.set_index("datetime")
        data_merged = data_merged.sort_index()
        data_merged.reset_index(inplace=True)
        data_merged.to_csv(
            dir_out + sub_dir_.split("/")[-1] + "_merged.csv", index=False
        )
    print(f"{len(sub_dir)} folders merged")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Description for arguments")
    parser.add_argument("dir_in", help="Input directory", type=str)
    parser.add_argument("dir_out", help="Output directory", type=str)
    argument = parser.parse_args()

    merge_sensor_data(argument.dir_in, argument.dir_out)

    print("Finished merging files")
