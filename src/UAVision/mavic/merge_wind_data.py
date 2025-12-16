import pandas as pd
import glob
import os
import argparse
from os import PathLike


def merge_wind_data(dir_in: str | PathLike[str], dir_out: str | PathLike[str]) -> None:
    """
    Merge wind data from multiple CSV files.

    dir_in: input directory containing wind CSV files
    dir_out: output directory for merged wind CSV file
    return: None
    """
    dir_in = str(dir_in).replace("\\", "/") + "/"
    dir_out = str(dir_out).replace("\\", "/") + "/"

    file_path_wind = [x for x in glob.glob(dir_in + "/*.csv")]
    df = pd.DataFrame({})

    for file in file_path_wind:
        file_name = os.path.basename(file)
        start_time = pd.to_datetime(file_name[-23:-4], format="%Y-%m-%d_%H-%M-%S")
        df_ = pd.read_csv(file)
        df_["datetime"] = start_time + pd.to_timedelta(df_["Flight time"])
        df = pd.concat([df, df_], ignore_index=True)

    df.to_csv(dir_out + "wind_merged.csv", index=False)
    print(f"{len(file_path_wind)} files merged")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Description for arguments")
    parser.add_argument("dir_in", help="Input directory", type=str)
    parser.add_argument("dir_out", help="Output directory", type=str)
    argument = parser.parse_args()

    merge_wind_data(argument.dir_in, argument.dir_out)

    print("Finished merging files")
